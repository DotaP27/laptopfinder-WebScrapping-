import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import csv

def fetch_and_save_to_file(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r.text)

def get_user_preferences():
    root = tk.Tk()
    root.title("Laptop Filter Options")
    root.geometry("400x400")
    # Options for dropdowns
    brands = ["Any", "Intel", "HP", "Dell", "Lenovo", "Asus", "Acer", "MSI"]
    rams = ["Any", "4GB", "8GB", "16GB", "32GB"]
    processors = ["Any", "i3", "i5", "i7", "Ryzen 3", "Ryzen 5", "Ryzen 7"]
    prices = ["Any", "30000", "40000", "50000", "60000", "75000", "100000"]
    ssd_var = tk.BooleanVar()
    screen_sizes = ["Any", "13", "14", "15.6", "17"]
    graphics = ["Any", "Integrated", "NVIDIA", "AMD"]
    battery = ["Any", "4", "6", "8", "10"]

    # Dropdowns
    brand_var = tk.StringVar(value=brands[0])
    ram_var = tk.StringVar(value=rams[0])
    processor_var = tk.StringVar(value=processors[0])
    price_var = tk.StringVar(value=prices[0])
    screen_var = tk.StringVar(value=screen_sizes[0])
    graphics_var = tk.StringVar(value=graphics[0])
    battery_var = tk.StringVar(value=battery[0])

    tk.Label(root, text="Select your laptop preferences:").pack(pady=10)
    tk.Label(root, text="Brand:").pack()
    tk.OptionMenu(root, brand_var, *brands).pack()
    tk.Label(root, text="RAM:").pack()
    tk.OptionMenu(root, ram_var, *rams).pack()
    tk.Label(root, text="Processor:").pack()
    tk.OptionMenu(root, processor_var, *processors).pack()
    tk.Label(root, text="Max Price:").pack()
    tk.OptionMenu(root, price_var, *prices).pack()
    tk.Checkbutton(root, text="SSD Required", variable=ssd_var).pack()
    tk.Label(root, text="Screen Size:").pack()
    tk.OptionMenu(root, screen_var, *screen_sizes).pack()
    tk.Label(root, text="Graphics Card:").pack()
    tk.OptionMenu(root, graphics_var, *graphics).pack()
    tk.Label(root, text="Min Battery Life (hours):").pack()
    tk.OptionMenu(root, battery_var, *battery).pack()

    def submit():
        root.quit()
        root.destroy()

    tk.Button(root, text="Submit", command=submit).pack(pady=20)
    root.mainloop()
    return (
        brand_var.get(),
        ram_var.get(),
        processor_var.get(),
        price_var.get(),
        "yes" if ssd_var.get() else "no",
        screen_var.get(),
        graphics_var.get(),
        battery_var.get()
    )

def export_to_csv(results, filename="filtered_laptops.csv"):
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["Title", "Image URL", "Flipkart Link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in results:
            writer.writerow({
                "Title": item.get("title", ""),
                "Image URL": item.get("img", ""),
                "Flipkart Link": item.get("link", "")
            })

def show_results_popup(results):
    import webbrowser
    root = tk.Tk()
    root.title("Filtered Laptops")
    root.geometry("600x500")
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    scroll_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    if not results:
        tk.Label(scroll_frame, text="No laptops found matching your criteria.").pack(pady=10)
    for item in results:
        frame = tk.Frame(scroll_frame, bd=2, relief=tk.RIDGE)
        frame.pack(fill=tk.X, padx=5, pady=5)
        if item["img"]:
            try:
                from PIL import Image, ImageTk
                import requests as req
                from io import BytesIO
                response = req.get(item["img"])
                img_data = BytesIO(response.content)
                pil_img = Image.open(img_data).resize((80, 80))
                tk_img = ImageTk.PhotoImage(pil_img)
                img_label = tk.Label(frame, image=tk_img)
                img_label.image = tk_img
                img_label.pack(side=tk.LEFT, padx=5)
            except Exception:
                pass
        tk.Label(frame, text=item["title"], wraplength=400, justify=tk.LEFT).pack(side=tk.LEFT, padx=5)
        if item["link"]:
            def open_link(url=item["link"]):
                webbrowser.open(url)
            link_btn = tk.Button(frame, text="View on Flipkart", command=open_link)
            link_btn.pack(side=tk.RIGHT, padx=5)
    def export_csv():
        export_to_csv(results)
        tk.messagebox.showinfo("Export", "Results exported to filtered_laptops.csv")
    tk.Button(root, text="Export to CSV", command=export_csv).pack(pady=10)
    tk.Button(root, text="Close", command=root.destroy).pack(pady=10)
    root.mainloop()

def scrape_product_titles(url, num_pages=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    all_blocks = []
    for page in range(1, num_pages + 1):
        page_url = url + f"&page={page}"
        try:
            r = requests.get(page_url, headers=headers, timeout=10)
            r.raise_for_status()
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            from tkinter import messagebox
            messagebox.showerror("Network Error", f"Could not fetch data from Flipkart page {page}.\nError: {e}")
            root.destroy()
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        all_blocks.extend(soup.find_all("div", class_="Otbq5D"))
    brand, ram, processor, price, ssd, screen_size, graphics, battery = get_user_preferences()
    filtered = []
    for block in all_blocks:
        title_tag = block.find_next("div", class_="KzDlHZ")
        img_tag = block.find("img")
        link_tag = block.find_parent("a", href=True)
        title = title_tag.get_text(strip=True) if title_tag else ""
        img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
        link_url = "https://www.flipkart.com" + link_tag["href"] if link_tag else ""
        # Filtering logic
        if brand and brand != "Any" and brand.lower() not in title.lower():
            continue
        if ram and ram != "Any" and ram.replace(' ', '').lower() not in title.replace(' ', '').lower():
            continue
        if processor and processor != "Any" and processor.lower() not in title.lower():
            continue
        if ssd == "yes" and "ssd" not in title.lower():
            continue
        if screen_size and screen_size != "Any" and screen_size.replace(' ', '') not in title.replace(' ', ''):
            continue
        if graphics and graphics != "Any" and graphics.lower() not in title.lower():
            continue
        filtered.append({"title": title, "img": img_url, "link": link_url})
    with open("data/flipkart_titles.txt", "w", encoding="utf-8") as f:
        for item in filtered:
            f.write(item["title"] + "\n")
    show_results_popup(filtered)

def launch_laptop_finder_app():
    import webbrowser
    from tkinter import ttk
    from PIL import Image, ImageTk
    import requests as req
    from io import BytesIO

    root = tk.Tk()
    root.title("💻 Laptop Finder ✨")
    root.geometry("950x650")
    root.configure(bg="#f7f6fd")

    sidebar = tk.Frame(root, width=270, bg="#a18cd1")
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    main_area = tk.Frame(root, bg="#f7f6fd")
    main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Label(sidebar, text="💻 Laptop Finder ✨", font=("Poppins", 22, "bold"), bg="#a18cd1", fg="#fff").pack(pady=25)

    brands = ["Any", "Intel", "HP", "Dell", "Lenovo", "Asus", "Acer", "MSI"]
    rams = ["Any", "4GB", "8GB", "16GB", "32GB"]
    processors = ["Any", "i3", "i5", "i7", "Ryzen 3", "Ryzen 5", "Ryzen 7"]
    prices = ["Any", "30000", "40000", "50000", "60000", "75000", "100000"]
    ssd_var = tk.BooleanVar()
    screen_sizes = ["Any", "13", "14", "15.6", "17"]
    graphics = ["Any", "Integrated", "NVIDIA", "AMD"]
    battery = ["Any", "4", "6", "8", "10"]

    brand_var = tk.StringVar(value=brands[0])
    ram_var = tk.StringVar(value=rams[0])
    processor_var = tk.StringVar(value=processors[0])
    price_var = tk.StringVar(value=prices[0])
    screen_var = tk.StringVar(value=screen_sizes[0])
    graphics_var = tk.StringVar(value=graphics[0])
    battery_var = tk.StringVar(value=battery[0])

    def add_filter(label, var, options, emoji):
        tk.Label(sidebar, text=f"{emoji} {label}", font=("Poppins", 13, "bold"), bg="#a18cd1", fg="#fff", anchor="w").pack(fill=tk.X, padx=25, pady=(12,0))
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground='#fff', background='#fff', borderwidth=0, relief="flat", font=("Poppins", 11))
        cb = ttk.Combobox(sidebar, textvariable=var, values=options, state="readonly", font=("Poppins", 11))
        cb.pack(fill=tk.X, padx=25, pady=(0,5))
        cb.configure(style='TCombobox')

    add_filter("Brand", brand_var, brands, "🏷️")
    add_filter("RAM", ram_var, rams, "🧠")
    add_filter("Processor", processor_var, processors, "⚡")
    add_filter("Max Price", price_var, prices, "💸")
    tk.Checkbutton(sidebar, text="SSD Required 🗄️", variable=ssd_var, bg="#a18cd1", font=("Poppins", 12, "bold"), fg="#fff", selectcolor="#f7f6fd", activebackground="#a18cd1", activeforeground="#fff").pack(padx=25, pady=(10,0), anchor="w")
    add_filter("Screen Size", screen_var, screen_sizes, "📺")
    add_filter("Graphics Card", graphics_var, graphics, "🎮")
    add_filter("Min Battery Life (hrs)", battery_var, battery, "🔋")

    results_frame = tk.Frame(main_area, bg="#f7f6fd")
    results_frame.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(results_frame, bg="#f7f6fd", highlightthickness=0)
    scrollbar = tk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#f7f6fd")
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def search():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        url = "https://www.flipkart.com/search?q=laptop"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        all_blocks = []
        for page in range(1, 11):
            page_url = url + f"&page={page}"
            try:
                r = requests.get(page_url, headers=headers, timeout=10)
                r.raise_for_status()
            except Exception as e:
                tk.messagebox.showerror("Network Error", f"Could not fetch data from Flipkart page {page}.\nError: {e}")
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            all_blocks.extend(soup.find_all("div", class_="Otbq5D"))
        filtered = []
        for block in all_blocks:
            title_tag = block.find_next("div", class_="KzDlHZ")
            img_tag = block.find("img")
            link_tag = block.find_parent("a", href=True)
            title = title_tag.get_text(strip=True) if title_tag else ""
            img_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
            link_url = "https://www.flipkart.com" + link_tag["href"] if link_tag else ""
            if brand_var.get() != "Any" and brand_var.get().lower() not in title.lower():
                continue
            if ram_var.get() != "Any" and ram_var.get().replace(' ', '').lower() not in title.replace(' ', '').lower():
                continue
            if processor_var.get() != "Any" and processor_var.get().lower() not in title.lower():
                continue
            if ssd_var.get() and "ssd" not in title.lower():
                continue
            if screen_var.get() != "Any" and screen_var.get().replace(' ', '') not in title.replace(' ', ''):
                continue
            if graphics_var.get() != "Any" and graphics_var.get().lower() not in title.lower():
                continue
            filtered.append({"title": title, "img": img_url, "link": link_url})
        if not filtered:
            tk.Label(scroll_frame, text="No laptops found matching your criteria.", bg="#f7f6fd", font=("Poppins", 15, "bold"), fg="#a18cd1").pack(pady=30)
        for item in filtered:
            frame = tk.Frame(scroll_frame, bg="#fff", highlightbackground="#e0e0e0", highlightthickness=2)
            frame.pack(fill=tk.X, padx=18, pady=14, ipadx=8, ipady=8)
            if item["img"]:
                try:
                    response = req.get(item["img"])
                    img_data = BytesIO(response.content)
                    pil_img = Image.open(img_data).resize((90, 90))
                    tk_img = ImageTk.PhotoImage(pil_img)
                    img_label = tk.Label(frame, image=tk_img, bg="#fff")
                    img_label.image = tk_img
                    img_label.pack(side=tk.LEFT, padx=12)
                except Exception:
                    pass
            tk.Label(frame, text=item["title"], wraplength=520, justify=tk.LEFT, bg="#fff", font=("Poppins", 13), fg="#333").pack(side=tk.LEFT, padx=12)
            if item["link"]:
                def open_link(url=item["link"]):
                    webbrowser.open(url)
                link_btn = tk.Button(frame, text="View on Flipkart 🔗", command=open_link, bg="#ff61a6", fg="#fff", font=("Poppins", 11, "bold"), relief=tk.FLAT, activebackground="#ff85c0", activeforeground="#fff", cursor="hand2")
                link_btn.pack(side=tk.RIGHT, padx=12)
    search_btn = tk.Button(sidebar, text="🔍 Search", command=search, bg="#6a82fb", fg="#fff", font=("Poppins", 15, "bold"), relief=tk.FLAT, activebackground="#a18cd1", activeforeground="#fff", cursor="hand2")
    search_btn.pack(pady=32, padx=25, fill=tk.X)

    def export_csv():
        results = []
        for frame in scroll_frame.winfo_children():
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("wraplength") == 520:
                    title = widget.cget("text")
                    img = None
                    link = None
                    for w in frame.winfo_children():
                        if isinstance(w, tk.Label) and hasattr(w, "image"):
                            img = w.image
                        if isinstance(w, tk.Button):
                            link = w.cget("command")
                    results.append({"title": title, "img": img, "link": link})
        export_to_csv(results)
        tk.messagebox.showinfo("Export", "Results exported to filtered_laptops.csv")
    tk.Button(sidebar, text="📤 Export to CSV", command=export_csv, bg="#43e97b", fg="#fff", font=("Poppins", 13, "bold"), relief=tk.FLAT, activebackground="#38f9d7", activeforeground="#fff", cursor="hand2").pack(pady=10, padx=25, fill=tk.X)

    root.mainloop()

if __name__ == "__main__":
    launch_laptop_finder_app()