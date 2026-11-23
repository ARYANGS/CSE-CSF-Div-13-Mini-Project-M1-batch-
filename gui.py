import calendar
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import tracker

FONT_FAMILY = "Segoe UI"
COLOR_BG = "#F5F6F8"
COLOR_TEXT = "#111827"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_ACCENT = "#2563EB"
COLOR_ACCENT_HOVER = "#1D4ED8"
COLOR_SECONDARY_HOVER = "#F3F4F6"
COLOR_DANGER_TEXT = "#991B1B"
COLOR_WARNING_TEXT = "#92400E"
COLOR_SUCCESS_TEXT = "#16A34A"

documents = tracker.load_documents()
is_sorted = False
search_placeholder_active = True

def create_button(parent, text, command, style_type="secondary"):
    if style_type == "primary":
        bg_norm, fg_norm, bg_hov, fg_hov = COLOR_ACCENT, "#FFFFFF", COLOR_ACCENT_HOVER, "#FFFFFF"
        btn = tk.Label(parent, text=text, bg=bg_norm, fg=fg_norm, font=(FONT_FAMILY, 10, "bold"),
                       padx=14, pady=6, cursor="hand2", relief="flat")
    else:
        bg_norm, fg_norm = "#FFFFFF", COLOR_TEXT
        bg_hov, fg_hov = ("#FEF2F2", "#DC2626") if style_type == "delete" else (COLOR_SECONDARY_HOVER, COLOR_TEXT)
        btn = tk.Label(parent, text=text, bg=bg_norm, fg=fg_norm, font=(FONT_FAMILY, 10), padx=14, pady=5,
                       cursor="hand2", relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER)
    btn.bind("<Enter>", lambda e: btn.config(bg=bg_hov, fg=fg_hov))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg_norm, fg=fg_norm))
    btn.bind("<Button-1>", lambda e: command())
    return btn

def create_card(parent, label_text, color):
    frame = tk.Frame(parent, bg="#FFFFFF", highlightthickness=1, highlightbackground=COLOR_BORDER, padx=16, pady=8)
    num_lbl = tk.Label(frame, text="0", font=(FONT_FAMILY, 18, "bold"), fg=color, bg="#FFFFFF")
    num_lbl.pack(anchor="w")
    tk.Label(frame, text=label_text, font=(FONT_FAMILY, 9), fg=COLOR_MUTED, bg="#FFFFFF").pack(anchor="w")
    return frame, num_lbl

def update_summary_cards():
    counts = {"Valid": 0, "Expiring Soon": 0, "Expired": 0}
    for doc in documents:
        st = tracker.get_status(tracker.get_days_remaining(doc["expiry_date"]))
        if st in counts:
            counts[st] = counts[st] + 1
    valid_num_label.config(text=str(counts["Valid"]))
    soon_num_label.config(text=str(counts["Expiring Soon"]))
    expired_num_label.config(text=str(counts["Expired"]))

def get_search_query():
    return "" if search_placeholder_active else search_entry.get().strip().lower()

def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
    query, sel_st = get_search_query(), status_combo.get()
    filtered = []
    for doc in documents:
        m_search = query == "" or (query in doc["name"].lower()) or (query in doc["document_type"].lower())
        days = tracker.get_days_remaining(doc["expiry_date"])
        status = tracker.get_status(days)
        m_status = sel_st == "All" or status == sel_st
        if m_search and m_status:
            filtered.append(doc)

    display_docs = sorted(filtered, key=tracker.get_expiry) if is_sorted else filtered
    tag_map = {"Expired": "expired", "Expiring Soon": "soon", "Valid": "valid"}
    for doc in display_docs:
        days = tracker.get_days_remaining(doc["expiry_date"])
        status = tracker.get_status(days)
        tree.insert("", "end", values=(doc["id"], doc["name"], doc["document_type"], doc["expiry_date"], days, status),
                    tags=(tag_map.get(status, "valid"),))

    count = len(display_docs)
    count_label.config(text="1 document" if count == 1 else f"{count} documents")

def toggle_sort():
    global is_sorted
    is_sorted = not is_sorted
    sort_btn.config(text="Sort by expiry: On" if is_sorted else "Sort by expiry")
    refresh_table()

def get_selected_document():
    selected = tree.selection()
    if not selected:
        return None
    item = tree.item(selected[0])
    doc_id = item["values"][0]
    for doc in documents:
        if doc["id"] == doc_id:
            return doc
    return None

def on_edit():
    doc = get_selected_document()
    if doc is None:
        messagebox.showinfo("Select Document", "Please select a document to edit.")
        return
    open_dialog(doc)

def on_delete():
    doc = get_selected_document()
    if doc is None:
        messagebox.showinfo("Select Document", "Please select a document to delete.")
        return
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{doc['name']}'?"):
        documents.remove(doc)
        tracker.save_documents(documents)
        refresh_table()
        update_summary_cards()

def open_date_picker(parent, target_entry):
    picker = tk.Toplevel(parent)
    picker.title("Select Date")
    picker.configure(bg="#FFFFFF")
    picker.transient(parent)
    picker.grab_set()
    picker.resizable(False, False)
    picker.geometry(f"290x270+{parent.winfo_x() + 50}+{parent.winfo_y() + 60}")

    try:
        cur_date = datetime.datetime.strptime(target_entry.get().strip(), "%Y-%m-%d").date()
    except Exception:
        cur_date = datetime.date.today()

    cal_data = {"year": cur_date.year, "month": cur_date.month}
    nav_bar = tk.Frame(picker, bg="#FFFFFF", padx=8, pady=8)
    nav_bar.pack(fill="x")
    month_label = tk.Label(nav_bar, font=(FONT_FAMILY, 10, "bold"), bg="#FFFFFF", fg=COLOR_TEXT)
    days_grid = tk.Frame(picker, bg="#FFFFFF", padx=8, pady=4)
    days_grid.pack(fill="both", expand=True)

    def redraw_calendar():
        for widget in days_grid.winfo_children():
            widget.destroy()
        month_label.config(text=f"{calendar.month_name[cal_data['month']]} {cal_data['year']}")
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for c in range(7):
            tk.Label(days_grid, text=weekdays[c], font=(FONT_FAMILY, 8, "bold"), fg=COLOR_MUTED, bg="#FFFFFF", width=4).grid(row=0, column=c, pady=(0, 4))
        for r, week in enumerate(calendar.monthcalendar(cal_data["year"], cal_data["month"])):
            for c, day_num in enumerate(week):
                if day_num != 0:
                    btn = tk.Label(days_grid, text=str(day_num), font=(FONT_FAMILY, 9), bg="#FFFFFF", fg=COLOR_TEXT, width=4, height=1, cursor="hand2")
                    btn.grid(row=r + 1, column=c, padx=1, pady=1)
                    btn.bind("<Button-1>", lambda e, d=day_num: on_select_day(d))
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLOR_ACCENT, fg="#FFFFFF"))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#FFFFFF", fg=COLOR_TEXT))

    def on_select_day(day):
        formatted_date = f"{cal_data['year']:04d}-{cal_data['month']:02d}-{day:02d}"
        target_entry.delete(0, tk.END)
        target_entry.insert(0, formatted_date)
        picker.destroy()

    def step_month(delta):
        m = cal_data["month"] + delta
        if m < 1:
            cal_data["month"], cal_data["year"] = 12, cal_data["year"] - 1
        elif m > 12:
            cal_data["month"], cal_data["year"] = 1, cal_data["year"] + 1
        else:
            cal_data["month"] = m
        redraw_calendar()

    def step_year(delta):
        cal_data["year"] = cal_data["year"] + delta
        redraw_calendar()

    for text, cmd in [("<<", lambda: step_year(-1)), ("<", lambda: step_month(-1))]:
        b = tk.Label(nav_bar, text=text, font=(FONT_FAMILY, 9, "bold"), bg="#FFFFFF", fg=COLOR_MUTED, cursor="hand2", padx=4)
        b.pack(side="left")
        b.bind("<Button-1>", lambda e, c=cmd: c())

    for text, cmd in [(">>", lambda: step_year(1)), (">", lambda: step_month(1))]:
        b = tk.Label(nav_bar, text=text, font=(FONT_FAMILY, 9, "bold"), bg="#FFFFFF", fg=COLOR_MUTED, cursor="hand2", padx=4)
        b.pack(side="right")
        b.bind("<Button-1>", lambda e, c=cmd: c())

    month_label.pack(side="left", expand=True)
    redraw_calendar()

def open_dialog(doc_to_edit=None):
    dialog = tk.Toplevel(root)
    dialog.configure(bg=COLOR_BG)
    is_edit = doc_to_edit is not None
    dialog.title("Edit Document" if is_edit else "Add Document")
    dialog.transient(root)
    dialog.grab_set()
    dialog.resizable(False, False)

    width, height = 440, 480
    x = root.winfo_x() + (root.winfo_width() - width) // 2
    y = root.winfo_y() + (root.winfo_height() - height) // 2
    dialog.geometry(f"{width}x{height}+{x}+{y}")

    form = tk.Frame(dialog, bg=COLOR_BG, padx=24, pady=16)
    form.pack(fill="both", expand=True)

    tk.Label(form, text="Name", font=(FONT_FAMILY, 9), fg=COLOR_MUTED, bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
    name_entry = ttk.Entry(form, style="Custom.TEntry")
    name_entry.pack(fill="x", pady=(0, 10))

    tk.Label(form, text="Document type", font=(FONT_FAMILY, 9), fg=COLOR_MUTED, bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
    doc_types = ["Passport", "Driving Licence", "National ID", "Insurance", "Vehicle Registration", "Visa", "Certificate", "Contract", "Other"]
    type_combo = ttk.Combobox(form, values=doc_types)
    type_combo.pack(fill="x", pady=(0, 10))

    tk.Label(form, text="Expiry date (YYYY-MM-DD)", font=(FONT_FAMILY, 9), fg=COLOR_MUTED, bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
    date_row = tk.Frame(form, bg=COLOR_BG)
    date_row.pack(fill="x", pady=(0, 10))
    date_entry = ttk.Entry(date_row, style="Custom.TEntry")
    date_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    date_btn = create_button(date_row, "Pick Date", lambda: open_date_picker(dialog, date_entry), style_type="secondary")
    date_btn.pack(side="right")

    tk.Label(form, text="Notes", font=(FONT_FAMILY, 9), fg=COLOR_MUTED, bg=COLOR_BG).pack(anchor="w", pady=(0, 2))
    notes_text = tk.Text(form, height=3, font=(FONT_FAMILY, 10), bg="#FFFFFF", fg=COLOR_TEXT,
                         relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER, wrap="word", padx=6, pady=6)
    notes_text.pack(fill="x", pady=(0, 10))

    if is_edit:
        name_entry.insert(0, doc_to_edit.get("name", ""))
        type_combo.set(doc_to_edit.get("document_type", ""))
        date_entry.insert(0, doc_to_edit.get("expiry_date", ""))
        notes_text.insert("1.0", doc_to_edit.get("notes", ""))

    error_label = tk.Label(form, text="", font=(FONT_FAMILY, 9), fg="#DC2626", bg=COLOR_BG)
    error_label.pack(anchor="w", pady=(0, 10))
    btn_row = tk.Frame(form, bg=COLOR_BG)
    btn_row.pack(fill="x")

    def on_save():
        name = name_entry.get().strip()
        doc_type = type_combo.get().strip()
        date_str = date_entry.get().strip()
        notes = notes_text.get("1.0", "end-1c").strip()

        if name == "" or doc_type == "":
            error_label.config(text="Name and document type cannot be empty.")
            return
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            error_label.config(text="Expiry date must be in YYYY-MM-DD format.")
            return

        if is_edit:
            doc_to_edit.update({"name": name, "document_type": doc_type, "expiry_date": date_str, "notes": notes})
        else:
            documents.append({
                "id": tracker.get_next_id(documents),
                "name": name,
                "document_type": doc_type,
                "expiry_date": date_str,
                "notes": notes
            })

        tracker.save_documents(documents)
        dialog.destroy()
        refresh_table()
        update_summary_cards()

    save_btn = create_button(btn_row, "Save", on_save, style_type="primary")
    save_btn.pack(side="right", padx=(8, 0))
    cancel_btn = create_button(btn_row, "Cancel", lambda: dialog.destroy(), style_type="secondary")
    cancel_btn.pack(side="right")

def on_search_focus(event, entering):
    global search_placeholder_active
    if entering and search_placeholder_active:
        search_entry.delete(0, tk.END)
        search_placeholder_active = False
    elif not entering and search_entry.get().strip() == "":
        search_entry.insert(0, "Search by name or type")
        search_placeholder_active = True

root = tk.Tk()
root.title("Document Expiry Tracker")
root.configure(bg=COLOR_BG)

win_w, win_h = 900, 600
scr_w, scr_h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"{win_w}x{win_h}+{(scr_w - win_w) // 2}+{(scr_h - win_h) // 2}")
root.minsize(750, 480)

style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.TEntry", fieldbackground="#FFFFFF", bordercolor=COLOR_BORDER, lightcolor=COLOR_BORDER, darkcolor=COLOR_BORDER, padding=6)
style.configure("TCombobox", fieldbackground="#FFFFFF", background="#FFFFFF", bordercolor=COLOR_BORDER, arrowcolor=COLOR_MUTED, padding=5)
style.configure("Treeview", background="#FFFFFF", foreground=COLOR_TEXT, rowheight=34, fieldbackground="#FFFFFF", font=(FONT_FAMILY, 10), borderwidth=0)
style.configure("Treeview.Heading", background="#F9FAFB", foreground="#374151", font=(FONT_FAMILY, 10, "bold"), relief="flat", borderwidth=0)
style.map("Treeview.Heading", background=[("active", "#F3F4F6")])
style.map("Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", "#1E40AF")])

top_frame = tk.Frame(root, bg=COLOR_BG, padx=16, pady=12)
top_frame.pack(fill="x")

title_label = tk.Label(top_frame, text="Document Expiry Tracker", font=(FONT_FAMILY, 16, "bold"), fg=COLOR_TEXT, bg=COLOR_BG)
title_label.pack(anchor="w", pady=(0, 8))

cards_frame = tk.Frame(top_frame, bg=COLOR_BG)
cards_frame.pack(anchor="w")

valid_card, valid_num_label = create_card(cards_frame, "Valid", COLOR_SUCCESS_TEXT)
soon_card, soon_num_label = create_card(cards_frame, "Expiring Soon", COLOR_WARNING_TEXT)
expired_card, expired_num_label = create_card(cards_frame, "Expired", COLOR_DANGER_TEXT)
for card in (valid_card, soon_card, expired_card):
    card.pack(side="left", padx=(0, 10))

toolbar = tk.Frame(root, bg=COLOR_BG, padx=16, pady=6)
toolbar.pack(fill="x")

search_entry = ttk.Entry(toolbar, style="Custom.TEntry", width=28)
search_entry.insert(0, "Search by name or type")
search_entry.bind("<FocusIn>", lambda e: on_search_focus(e, True))
search_entry.bind("<FocusOut>", lambda e: on_search_focus(e, False))
search_entry.bind("<KeyRelease>", lambda e: refresh_table())
search_entry.pack(side="left", padx=(0, 10))

status_combo = ttk.Combobox(toolbar, values=["All", "Valid", "Expiring Soon", "Expired"], state="readonly", width=14)
status_combo.set("All")
status_combo.bind("<<ComboboxSelected>>", lambda e: refresh_table())
status_combo.pack(side="left", padx=(0, 10))

sort_btn = create_button(toolbar, "Sort by expiry", toggle_sort, style_type="secondary")
sort_btn.pack(side="left")

add_btn = create_button(toolbar, "Add Document", lambda: open_dialog(), style_type="primary")
add_btn.pack(side="right")

table_container = tk.Frame(root, bg="#FFFFFF", highlightthickness=1, highlightbackground=COLOR_BORDER)
table_container.pack(fill="both", expand=True, padx=16, pady=(6, 0))

columns = ("id", "name", "type", "expiry_date", "days_left", "status")
tree = ttk.Treeview(table_container, columns=columns, show="headings")

cols_meta = [("id", "ID", 50, "center"), ("name", "Name", 220, "w"), ("type", "Type", 150, "w"),
             ("expiry_date", "Expiry Date", 120, "center"), ("days_left", "Days Left", 90, "center"),
             ("status", "Status", 130, "center")]
for cid, ctext, cw, canchor in cols_meta:
    tree.heading(cid, text=ctext)
    tree.column(cid, width=cw, anchor=canchor)

tree.tag_configure("valid", background="#FFFFFF", foreground="#111827")
tree.tag_configure("soon", background="#FEF3C7", foreground="#92400E")
tree.tag_configure("expired", background="#FEE2E2", foreground="#991B1B")

scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(fill="both", expand=True)

tree.bind("<Double-1>", lambda e: on_edit())

bottom_bar = tk.Frame(root, bg=COLOR_BG, padx=16, pady=12)
bottom_bar.pack(fill="x", side="bottom")

edit_btn = create_button(bottom_bar, "Edit", on_edit, style_type="secondary")
edit_btn.pack(side="left", padx=(0, 8))

delete_btn = create_button(bottom_bar, "Delete", on_delete, style_type="delete")
delete_btn.pack(side="left")

count_label = tk.Label(bottom_bar, text="0 documents", font=(FONT_FAMILY, 9), fg=COLOR_MUTED, bg=COLOR_BG)
count_label.pack(side="right")

update_summary_cards()
refresh_table()

if __name__ == "__main__":
    root.mainloop()
