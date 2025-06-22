import argparse
import os

MEMORIES_FILE = "memories.txt"

def add_memory(memory_text):
    """Adds a memory to the memories file."""
    with open(MEMORIES_FILE, "a") as f:
        f.write(memory_text + "\n")
    print("Memory added.")

def search_memories(search_term):
    """Searches for memories containing the search term."""
    if not os.path.exists(MEMORIES_FILE):
        print("No memories found. Add one first.")
        return

    print("Found memories:")
    found = False
    with open(MEMORIES_FILE, "r") as f:
        for line in f:
            if search_term.lower() in line.lower():
                print(f"- {line.strip()}")
                found = True
    
    if not found:
        print("No memories found matching your search.")

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description="A Shazam for your memories.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Add a new memory.")
    add_parser.add_argument("memory_text", type=str, help="The memory to add.")

    # 'search' command
    search_parser = subparsers.add_parser("search", help="Search your memories.")
    search_parser.add_argument("search_term", type=str, help="The term to search for.")

    args = parser.parse_args()

    if args.command == "add":
        add_memory(args.memory_text)
    elif args.command == "search":
        search_memories(args.search_term)

if __name__ == "__main__":
    main()
