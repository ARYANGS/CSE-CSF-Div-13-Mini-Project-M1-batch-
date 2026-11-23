import datetime
import json

EXPIRING_SOON_DAYS = 30

def load_documents():
    try:
        with open("documents.json", "r") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def save_documents(documents):
    with open("documents.json", "w") as file:
        json.dump(documents, file, indent=2)

def get_next_id(documents):
    highest_id = 0
    for doc in documents:
        if doc["id"] > highest_id:
            highest_id = doc["id"]
    return highest_id + 1

def get_days_remaining(expiry_date_str):
    expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
    return (expiry_date - datetime.date.today()).days

def get_status(days_remaining):
    if days_remaining < 0:
        return "Expired"
    elif days_remaining <= EXPIRING_SOON_DAYS:
        return "Expiring Soon"
    else:
        return "Valid"

def display_documents(documents):
    if len(documents) == 0:
        print("No documents found.")
        return
    print(f"{'ID':<6} {'Name':<22} {'Type':<18} {'Expiry Date':<14} {'Days Left':<12} {'Status':<15}")
    for doc in documents:
        days = get_days_remaining(doc["expiry_date"])
        status = get_status(days)
        print(f"{doc['id']:<6} {doc['name']:<22} {doc['document_type']:<18} {doc['expiry_date']:<14} {days:<12} {status:<15}")

def prompt_non_empty(prompt_text):
    while True:
        value = input(prompt_text).strip()
        if value != "":
            return value
        print("This field cannot be empty.")

def prompt_date(prompt_text):
    while True:
        date_str = input(prompt_text).strip()
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def find_document(documents, prompt_text):
    try:
        doc_id = int(input(prompt_text).strip())
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return None
    for doc in documents:
        if doc["id"] == doc_id:
            return doc
    print("Document not found.")
    return None

def add_document(documents):
    name = prompt_non_empty("Enter document name: ")
    doc_type = prompt_non_empty("Enter document type: ")
    expiry_date = prompt_date("Enter expiry date (YYYY-MM-DD): ")
    notes = input("Enter notes: ").strip()
    new_doc = {"id": get_next_id(documents), "name": name, "document_type": doc_type, "expiry_date": expiry_date, "notes": notes}
    documents.append(new_doc)
    save_documents(documents)
    print("Document added successfully.")

def edit_document(documents):
    if len(documents) == 0:
        print("No documents found.")
        return
    doc = find_document(documents, "Enter document ID to edit: ")
    if doc is None:
        return
    name = input(f"Enter new name (current: {doc['name']}): ").strip()
    if name != "":
        doc["name"] = name
    doc_type = input(f"Enter new type (current: {doc['document_type']}): ").strip()
    if doc_type != "":
        doc["document_type"] = doc_type
    while True:
        date_input = input(f"Enter new expiry date (current: {doc['expiry_date']}): ").strip()
        if date_input == "":
            break
        try:
            datetime.datetime.strptime(date_input, "%Y-%m-%d")
            doc["expiry_date"] = date_input
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    notes = input(f"Enter new notes (current: {doc['notes']}): ").strip()
    if notes != "":
        doc["notes"] = notes
    save_documents(documents)
    print("Document updated successfully.")

def delete_document(documents):
    if len(documents) == 0:
        print("No documents found.")
        return
    doc = find_document(documents, "Enter document ID to delete: ")
    if doc is None:
        return
    confirm = input("Are you sure you want to delete this document? (yes/no): ").strip().lower()
    if confirm in ("yes", "y"):
        documents.remove(doc)
        save_documents(documents)
        print("Document deleted successfully.")
    else:
        print("Deletion cancelled.")

def search_documents(documents):
    query = input("Enter search term: ").strip().lower()
    if query == "":
        print("Search term cannot be empty.")
        return
    results = []
    for doc in documents:
        if query in doc["name"].lower() or query in doc["document_type"].lower():
            results.append(doc)
    display_documents(results)

def filter_by_status(documents):
    choice = input("Filter by (1. Valid, 2. Expiring Soon, 3. Expired): ").strip()
    status_map = {"1": "Valid", "2": "Expiring Soon", "3": "Expired"}
    if choice not in status_map:
        print("Invalid choice.")
        return
    results = []
    for doc in documents:
        if get_status(get_days_remaining(doc["expiry_date"])) == status_map[choice]:
            results.append(doc)
    display_documents(results)

def get_expiry(doc):
    return doc["expiry_date"]

def show_sorted_documents(documents):
    display_documents(sorted(documents, key=get_expiry))

def show_attention_documents(documents):
    results = []
    for doc in documents:
        status = get_status(get_days_remaining(doc["expiry_date"]))
        if status in ("Expired", "Expiring Soon"):
            results.append(doc)
    display_documents(results)

def main():
    documents = load_documents()
    while True:
        print("\nDocument Expiry and Renewal Tracker")
        print("1. Add document\n2. View all documents\n3. Edit a document\n4. Delete a document\n"
              "5. Search by name or type\n6. Filter by status\n7. Show sorted by expiry date\n"
              "8. Show only documents needing attention (expired and expiring soon)\n9. Exit")
        choice = input("Enter choice (1-9): ").strip()
        if choice == "1":
            add_document(documents)
        elif choice == "2":
            display_documents(documents)
        elif choice == "3":
            edit_document(documents)
        elif choice == "4":
            delete_document(documents)
        elif choice == "5":
            search_documents(documents)
        elif choice == "6":
            filter_by_status(documents)
        elif choice == "7":
            show_sorted_documents(documents)
        elif choice == "8":
            show_attention_documents(documents)
        elif choice == "9":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main()
