# %% 
import re
import pandas as pd
import traceback

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common import exceptions as e
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# %%



class CatalogScraper:

    def __init__(self, url, file_name, split_char, nth, pattern_code=None):

        """
        Initialize the url, file name, character that it will be used to split the string,
        the nth characther occurrence where the string should be splitted, and the regex 
        pattern of the course code.

        Also the constants that contains the xpath to pagination, codes and names on the DOM tree.
        """
        self.url = url 
        self.file_name = file_name
        self.split_char = split_char
        self.nth = int(nth)
        self.pattern_code = pattern_code
        
    def _call_driver_and_get(self):

        self.driver = webdriver.Chrome(executable_path=r'driver\chromedriver.exe')

        try:
            self.driver.get(self.url)
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
            except:
                print(e)
                traceback.print_exc()
                pass
        except:
            print(e)
            traceback.print_exc()
            pass

    def _extract_codes_names(self):

        """ Extract the codes and names data.
        """

        self.PATTERN_CODE_DEFAULT = r'^[A-Z]+\s\d+'
        self.XPATH_PAGINATION = r'//span[@aria-current="page"]//following-sibling::a[1]'
        self.XPATH_CODES_NAMES = r'//div[@id="advanced_filter_section"]/following-sibling::table[@class="table_default"]//tr//td//a'
        self.original_codes_names = []
        
        self.next = self.driver.find_element(By.XPATH, self.XPATH_PAGINATION)

        try:

            while next:

                    codes_names_web_elem = self.driver.find_elements(By.XPATH, self.XPATH_CODES_NAMES)

                    for i, code_name in enumerate(codes_names_web_elem):
                        #print(code_name.text)
                        self.original_codes_names.append(code_name.text)

                    try:
                        self.next = self.driver.find_element(By.XPATH, self.XPATH_PAGINATION)
                        self.driver.get(self.next.get_attribute('href'))
                    
                    except:
                        self.driver.close()                        
                        break
        except:
            
            print(e)
            traceback.print_exc()
            
            pass
        
    def _transform_uppercase(self, name):
    

        """ Transforms an upper case string into title case. If there is a roman numerals the upper case 
        form will be reverted. 
        
        INPUT: An uppercase string.

        OUTPUT: A titlecase string.
        
        """
        
        ROMANS = {r'\bIi\b':r'II',
        r'\bIii\b':r'III',
        r'\bIv\b':r'IV',
        r'\bVi\b':r'VI',
        r'\bVii\b':r'VII',
        r'\bViii\b':r'VIII',
        r'\bIx\b':r'IX',
        r'\bXi\b':r'XI',
        r'\bXii\b':r'XII',
        r'\bXiii\b':r'XIII',
        r'\bXiv\b':r'XIV',
        r'\bXvi\b':r'XVI',
        r'\bXvii\b':r'XVII'}

        try:
            
            # TITLE CASE NAME
            name = name.title()

            # CORRECT ROMANS NUMERAL
            for roman_pattern, roman_upper in ROMANS.items():
                if re.search(roman_pattern, name):
                    name = re.sub(roman_pattern, roman_upper, name)       

        except:
            
            traceback.print_exc()
            pass

        return name
        
    
    def _split_and_transform(self):

        """ 1. Split each code cointained in codes_names list and append it on the codes_list list.
            2. Split each name cointained in codes_names.
            3. Proper case each name.
            4. Check if there is any roman numeral to be turned into upper case again.
            5. Append name on the names_list list.
            6. Create a uni code column from the file name and using the length of codes_list.
            7. Update uni_code_list, names_list, codes_list, codes_names_list
        """

        # original_codes_names, pattern_code, pattern_char_split, nth, file_name
        self.codes_list = []
        self.names_list = []
        self.codes_names_list = []
        self.uni_code_list = []

        if self.split_char == '\s':
            self.split_char = ' '

        for code_name in self.original_codes_names:

            try:
                if re.match(self.pattern_code, code_name):
                    #print(code_name)
                    self.codes_names_list.append(code_name)

                    # SPLIT AND APPEND CODE

                    # returns the index of all char split on code_name
                    indexes_split_char = [x.start() for x in re.finditer(self.split_char, code_name)]

                    # code part
                    code = code_name[0:indexes_split_char[self.nth - 1]]
                    self.codes_list.append(code)
                    #print(code)
                        
                    # SPLIT NAME
                    # name part                    
                    name = code_name[indexes_split_char[self.nth - 1] + 1:]
                    
                    if name.isupper():

                        name =  self._transform_uppercase(name)

                    else:
                        
                    # PROPER CASE NAME
                        name = ' '.join([w.title() if w.islower() else w for w in name.split()])

                    if re.search(r"'S", name):
                        name = re.sub(r"'S","'s", name)
                        
                        
                    if re.search(r' & ',name):
                        name = re.sub(r'&',r'And', name)

                    # APPEND NAME
                    self.names_list.append(name)
                    #print(name)

                    print('Code: {}\nName: {}\n\n'.format(code, name))
                    
            except:
                
                print(e)
                traceback.print_exc()
                print('Error split_and_transform: {}'.format(code_name))
                pass

        # UNI CODE LIST

        self.uni_code_list = [re.match(r"^\d+", self.file_name).group()] * len(self.codes_names_list)

    def create_spreadsheet(self):
        """
        Gets a file name and a DataFrame and converts into a excel file, and save it at excel_files folder.

        """
        try:
            EXCEL_FILES_PATH = r'excel_files'
            EXTENSION = '.xlsx'
            PATH_FILE = EXCEL_FILES_PATH + '/' + self.file_name + EXTENSION
            self.df.to_excel(PATH_FILE, index=False)

        except:
            
            print(e)
            traceback.print_exc()

    def _load(self):

        """1. Create a DataFrame using the uni code, names and codes lists.
        2. Transpose the DataFrame.
        3. Drop duplicates.
        4. Left align the columns.
        5. Trim all columns.
        6. Create a spreadsheet at excel_files directory using the file name provided.
        """

        try:
            # LOAD

            # Create DataFrame
            self.df = pd.DataFrame([self.uni_code_list, self.names_list, self.codes_list, self.codes_names_list], index=['uni_code', 'course_name', 'course_code', 'original_string'])

            # Transpose DataFrame
            self.df = self.df.T

            # Drop Duplicates
            self.df.drop_duplicates(inplace = True)

            # Left align
            self.df.style.set_properties(**{'text-align': 'left'})

            # Trim DataFrame
            trim_strings = lambda x: x.strip() if isinstance(x, str) else x
            self.df = self.df.applymap(trim_strings)

            try: 
                # Create Spreadsheet
                self.create_spreadsheet()
                
            except:
                
                print(e)
                traceback.print_exc()

        except:
            
            print(e)
            traceback.print_exc()

# %%
class CatalogUniversitiesList(CatalogScraper):

    def __init__(self):
        
        self._df = pd.read_excel(r'source_spreadsheet\Catalog Unis.xlsx')


        """
        self._file_names = self._df[self._df.loc[:,'status'].str.startswith('1')]['file_name']
        self._pattern_code = self._df[self._df.loc[:,'status'].str.startswith('1')]['pattern_code']
        self._urls = self._df[self._df.loc[:,'status'].str.startswith('1')]['url'] 
        """
        
        self._indexes = self._df.index[self._df.loc[:,'status'].str.startswith('1')]
            
    def _call_catalog_scraper(self):

        for i, index in enumerate(self._indexes):
            
            print('=================================================')

            print('#: {}/{}\nsetting variables...'.format(i+1,len(self._indexes)))

            self.url = self._df.iloc[index,1:6][0]
            self.file_name = self._df.iloc[index,1:6][1]
            self.split_char = self._df.iloc[index,1:6][2]
            self.nth = int(self._df.iloc[index,1:6][3])
            self.pattern_code = self._df.iloc[index,1:6][4] 


            print('variables ready.')
            
            print('\n\nrow: {}\nurl: {}\nfile_name: {}\nsplit_char: {}\nnth: {}\npattern_code: {}'
            .format(index, self.url,self.file_name, self.split_char, self.nth, self.pattern_code))
            
            print('\n\ncalling driver...')

            self._call_driver_and_get()

            print('driver ready.\n\nstarting extraction...')

            self._extract_codes_names()

            print('extraction done.\n\nstarting transformation...')

            self._split_and_transform()

            print('transformation done.\n\nstarting load...')

            self._load()
            
            print('load done.')

# %%
