from tkinter import *
from tkinter import ttk, simpledialog
from pymongo import MongoClient
from datetime import datetime

class ReportsPage(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Connect to MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["CaneCheck"]
        self.collection = self.db["Session"]

        # Search Frame
        search_frame = Frame(self, bg="lightgrey")
        search_frame.pack(pady=10)
        
        # Session Name Label
        session_name_label = Label(search_frame, text="Edit Session Name:", font=("Arial", 14))
        session_name_label.grid(row=0, column=0, padx=(5, 10), pady=5)
        
        # Session Name Entry
        self.session_name_entry = Entry(search_frame, width=30, font=("Arial", 12))
        self.session_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Edit Button
        edit_button = Button(search_frame, text="Edit", command=self.edit_session_name, bg="#9E8DB9", fg="white", font=("Arial", 14), relief=RAISED)
        edit_button.grid(row=0, column=2, padx=(0, 10), pady=5)
        
        # Search Entry
        self.search_entry = Entry(search_frame, width=40, font=("Arial", 16))
        self.search_entry.grid(row=1, column=0, columnspan=2, padx=(5, 0), pady=5)
        
        # Search Button
        search_button = Button(search_frame, text="Search", command=self.perform_search, bg="#9E8DB9", fg="white", font=("Arial", 14), relief=RAISED)
        search_button.grid(row=1, column=2, padx=(0, 10), pady=5)

        # Creating the table
        self.table = ttk.Treeview(self, columns=("SessionName", "ElapsedTime"), show="headings", height=3)
        self.table.heading("SessionName", text="Session Name")
        self.table.heading("ElapsedTime", text="Elapsed Time")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="lightgrey")
        style.map("Treeview", background=[("selected", "lightblue")])
        self.table.pack(pady=20)

        # Inserting data from MongoDB
        self.fetch_data_from_mongodb()

    def perform_search(self):
        search_query = self.search_entry.get()
        for row in self.table.get_children():
            self.table.delete(row)
        try:
            search_query = int(search_query)
            data = self.collection.find({"Session_ID": search_query})
        except ValueError:
            data = self.collection.find({"SessionName": {"$regex": search_query, "$options": "i"}})
        for row in data:
            session_name = row.get("SessionName", "")
            start_time = self.parse_datetime(row.get("StartTime", ""))
            end_time = self.parse_datetime(row.get("EndTime", ""))
            elapsed_time = end_time - start_time
            self.table.insert("", "end", values=(session_name, elapsed_time))
            self.table.tag_configure(session_name, foreground="blue", font=("Arial", 10, "underline"))
            self.table.tag_bind(session_name, "<Button-1>", lambda event, name=session_name: self.edit_session(session_name))

    def fetch_data_from_mongodb(self):
        data = self.collection.find()
        for row in data:
            session_name = row.get("SessionName", "")
            start_time = self.parse_datetime(row.get("StartTime", ""))
            end_time = self.parse_datetime(row.get("EndTime", ""))
            elapsed_time = end_time - start_time
            self.table.insert("", "end", values=(session_name, elapsed_time))
            self.table.tag_configure(session_name, foreground="blue", font=("Arial", 10, "underline"))
            self.table.tag_bind(session_name, "<Button-1>", lambda event, name=session_name: self.edit_session(session_name))

    def parse_datetime(self, datetime_str):
        formats = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                pass
        raise ValueError(f"Unable to parse datetime: {datetime_str}")

    def edit_session(self, session_name):
        print(f"Editing session with name: {session_name}")

    def edit_session_name(self):
        selected_items = self.table.selection()
        if selected_items:
            selected_session_name = self.table.item(selected_items[0], "values")[0]
            new_session_name = simpledialog.askstring("Edit Session Name", f"Enter new name for session '{selected_session_name}':")
            if new_session_name:
                # Perform database update with new session name
                print(f"Updating session name from '{selected_session_name}' to '{new_session_name}'")

    def exit_app(self):
        self.client.close()
        self.parent.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title("Reports Page")
    root.geometry("800x600")
    root.configure(bg="white")
    
    reports_page = ReportsPage(root)
    reports_page.pack(fill="both", expand=True)
    
    root.mainloop()
