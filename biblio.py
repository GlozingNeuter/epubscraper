import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import csv
import argparse
from pathlib import Path
import tqdm
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="Path to epub to scrap")
parser.add_argument("-s", "--selector", dest="selector", type=str, help="Choose a CSS selector for footnotes", default=".footnote")
parser.add_argument("-o", "--output", dest="output", type=str, help="Path to output file", default="./outputs/output.csv")
args = parser.parse_args()

path = Path(args.path)
output_path = Path(args.output)
selector = args.selector

def follow_backlink(csv_path):
    with open(csv_path) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter="|")
        for row in csv_reader:
            print(row[3])

def scrape_epub(path):
    book = epub.read_epub(path)
    with open(output_path, "w", newline="") as csvfile:
        title = book.get_metadata("DC", "title")
        writer = csv.writer(csvfile, delimiter="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["title", "note", "item_name", "backlink", "path", "context"])
        for item in tqdm(book.get_items()):
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                item_name = item.get_name()
                item_content = item.get_body_content()    
                html_soup = BeautifulSoup(item_content)
                for data in html_soup.select(selector):
                    note = data.get_text()
                    try: 
                        backlink = data.p.a["href"]
                        if ".xhtml" not in backlink:
                            try: 
                                context = html_soup.find(id = backlink[1:]).parent
                                print(backlink[1:])
                                print("Context: " + context)
                            except AttributeError:
                                context = "Context not found"
                        else :
                            link = backlink.split("#")
                            context_item = book.get_item_with_href(link[0])
                            context = BeautifulSoup(context_item.get_body_content()).find(id = link[1]).parent


                    except TypeError:
                        print("Error: No backlink in note")
                    
                    writer.writerow([title, note, item_name, backlink, path, context])
    
scrape_epub(path)
#follow_backlink("outputs/output.csv")





