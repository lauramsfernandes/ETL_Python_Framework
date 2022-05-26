# %%
from catalog import cat_module as cat
# %%

url = r'https://bulletin.capital.edu/content.php?catoid=16&navoid=584'
file_name = r'9998_Capital_University_Under'
split_char = r'-'
nth = 1
pattern_code = r'^[A-Z]+'
scraper = cat.CatalogScraper(url, file_name, split_char, nth, pattern_code)

# %%
scraper._call_driver_and_get()
scraper._extract_codes_names()
scraper._split_and_transform()
scraper._load()


# %%
scraper =  cat.CatalogUniversitiesList()
# %%
scraper._call_catalog_scraper()

# %%
scraper._load()
# %%
git config user.email "lauramsfernandes@gmail.com"
git config user.name "Laura Fernandes"
# %%
