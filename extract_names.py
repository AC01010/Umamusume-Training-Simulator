import json

def extract_names_from_carddb():
    """Extract cardName and fullName from cardDB.json and save to txt file"""
    
    try:
        # Read the JSON file
        with open('cardDB.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract all unique names
        names_set = set()
        
        # Iterate through all cards
        for card_id, card_data in data.items():
            if isinstance(card_data, dict):
                # Extract cardName if it exists
                if 'cardName' in card_data:
                    names_set.add(card_data['cardName'])
                
                # Extract fullName if it exists
                if 'fullName' in card_data:
                    names_set.add(card_data['fullName'])
        
        # Convert to sorted list
        names_list = sorted(list(names_set))
        
        # Save to txt file
        with open('chinese_names.txt', 'w', encoding='utf-8') as f:
            for name in names_list:
                f.write(name + '\n')
        
        print(f"Extracted {len(names_list)} unique names to chinese_names.txt")
        
        # Also print first 10 names for verification
        print("\nFirst 10 names:")
        for i, name in enumerate(names_list[:10]):
            print(f"{i+1}. {name}")
            
        return names_list
        
    except FileNotFoundError:
        print("Error: cardDB.json not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in cardDB.json")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    extract_names_from_carddb()