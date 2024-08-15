import requests
from bs4 import BeautifulSoup
import re
import random
import os

class RecipeScraper:
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        self.recipe_data = self._fetch_recipe_data()

    def _fetch_recipe_data(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.find('h1').get_text(strip=True)
            ingredients = self._extract_ingredients(soup)
            steps = self._extract_steps(soup)
            categories = self._extract_categories(soup)
            tags = self._extract_tags(soup)

            return {
                "title": title,
                "ingredients": ingredients,
                "steps": steps,
                "categories": categories,
                "tags": tags,
            }
        except Exception as e:
            print(f"Error fetching recipe: {e}")
            return None

    def _extract_ingredients(self, soup):
        ingredients = []
        for section in soup.find_all(class_=re.compile(r'\bingredients\b')):
            for ul in section.find_all('ul'):
                for li in ul.find_all('li'):
                    ingredients.append(li.get_text(strip=True))
        return ingredients

    def _extract_steps(self, soup):
        steps = []
        for ol in soup.find_all('ol'):
            for li in ol.find_all('li'):
                step = li.get_text(strip=True).replace("Serious Eats / Lorena Masso", "").replace("\n", " ")
                steps.append(step)
        return steps

    def _extract_categories(self, soup):
        categories = []
        category_section = soup.find(class_='categories')  # Adjust based on actual class or id
        if category_section:
            categories = [cat.get_text(strip=True) for cat in category_section.find_all('a')]
        return categories

    def _extract_tags(self, soup):
        tags = []
        tag_section = soup.find(class_='tags')  # Adjust based on actual class or id
        if tag_section:
            tags = [tag.get_text(strip=True) for tag in tag_section.find_all('a')]
        return tags

    def display_ingredients(self):
        print("Ingredients List:")
        for ingredient in self.recipe_data['ingredients']:
            print(f"- {ingredient}")

    def display_all_steps(self):
        print("Complete Preparation Steps:")
        for i, step in enumerate(self.recipe_data['steps']):
            print(f"Step {i + 1}: {step}")

    def search_online(self, query):
        formatted_query = query.replace(" ", "+")
        google_url = f"https://www.google.com/search?q={formatted_query}"
        youtube_url = f"https://www.youtube.com/results?search_query={formatted_query}"
        print(f"Search results for '{query}':\n* Google: {google_url}\n* YouTube: {youtube_url}")

    def navigate_steps(self):
        current_index = 0
        while True:
            self._show_step(current_index)
            action = input("1. Next\n2. Previous\n3. Exit\nChoose an option: ")
            if action == "1":
                if current_index < len(self.recipe_data['steps']) - 1:
                    current_index += 1
                else:
                    print("This is the last step.")
            elif action == "2":
                if current_index > 0:
                    current_index -= 1
                else:
                    print("This is the first step.")
            elif action == "3":
                print("Exiting...")
                break
            else:
                print("Invalid option. Try again.")

    def _show_step(self, index):
        if 0 <= index < len(self.recipe_data['steps']):
            print(f"Step {index + 1}: {self.recipe_data['steps'][index]}")
        else:
            print("Invalid step index.")

    def _sanitize_filename(self, title):
        """Sanitize the recipe title to create a valid filename."""
        return re.sub(r'[\/:*?"<>|]', '_', title) + '.txt'

    def save_recipe_to_file(self):
        if not self.recipe_data:
            print("No recipe data to save.")
            return
        
        title = self.recipe_data['title']
        filename = self._sanitize_filename(title)
        
        with open(filename, 'w') as file:
            file.write(f"Title: {title}\n\n")
            file.write("Ingredients:\n")
            for ingredient in self.recipe_data['ingredients']:
                file.write(f"- {ingredient}\n")
            file.write("\nPreparation Steps:\n")
            for i, step in enumerate(self.recipe_data['steps']):
                file.write(f"Step {i + 1}: {step}\n")
            if self.recipe_data.get('categories'):
                file.write("\nCategories:\n")
                for category in self.recipe_data['categories']:
                    file.write(f"- {category}\n")
            if self.recipe_data.get('tags'):
                file.write("\nTags:\n")
                for tag in self.recipe_data['tags']:
                    file.write(f"- {tag}\n")
        
        print(f"Recipe saved to {filename}.")

def get_recipe_suggestion():
    suggestions = [
        "https://www.allrecipes.com/recipe/38331/stuffed-eggplant/",
        "https://www.allrecipes.com/recipe/280246/chef-johns-tuna-noodle-casserole/",
        "https://www.seriouseats.com/jamaican-banana-fritters-recipe-7498871",
        "https://www.seriouseats.com/red-eye-gravy-recipe-8640434",
        "https://www.seriouseats.com/lemon-ricotta-cake-recipe-8551536"
    ]
    return random.choice(suggestions)

def main():
    print("Welcome to the Recipe Assistant!")
    print("1. Enter Recipe URL")
    print("2. Suggest a Recipe")
    choice = input("Choose an option: ")

    if choice == "1":
        url = input("Enter the recipe URL: ")
        scraper = RecipeScraper(url)
    elif choice == "2":
        suggested_url = get_recipe_suggestion()
        print(f"Suggested Recipe URL: {suggested_url}")
        url_choice = input("Would you like to use this URL? (yes/no): ")
        if url_choice.lower() == "yes":
            scraper = RecipeScraper(suggested_url)
        else:
            print("No URL selected. Exiting.")
            return
    else:
        print("Invalid choice. Exiting.")
        return

    if scraper.recipe_data:
        print("\nWhat would you like to do?")
        print("1. Display Ingredients")
        print("2. Show Preparation Steps")
        print("3. Show All Steps")
        print("4. Search Online")
        print("5. Save Full Recipe (Text File)")
        user_choice = input("Enter your choice: ")

        if user_choice == "1":
            scraper.display_ingredients()
        elif user_choice == "2":
            scraper.navigate_steps()
        elif user_choice == "3":
            scraper.display_all_steps()
        elif user_choice == "4":
            query = input("Enter search query: ")
            scraper.search_online(query)
        elif user_choice == "5":
            scraper.save_recipe_to_file()
        else:
            print("Invalid choice.")
    else:
        print("Failed to retrieve recipe.")

if __name__ == "__main__":
    main()
