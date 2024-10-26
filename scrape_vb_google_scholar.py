#!/usr/bin/env python
# coding: utf-8

# # Scrape Vb Google Scholar

# In[1]:


import __main__ as main
import subprocess as sp
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
notebook_name = 'scrape_vb_google_scholar'

if not hasattr(main, '__file__'):
    sp.run(f"jupyter nbconvert --to script '{notebook_name}.ipynb'; chmod u+x {notebook_name}.py", shell=True)


# In[2]:


vineet_google_scholar = 'https://scholar.google.com/citations?hl=en&user=zr2I_WMAAAAJ&view_op=list_works&sortby=pubdate'
sp.run(f"cd publications; wget '{vineet_google_scholar}' -O gscholar_hits.html", shell=True)


# In[3]:


with open("publications/gscholar_hits.html", 'rb') as infile:
    hits = infile.read()
hits = hits.decode('unicode-escape')


# In[4]:


publications = re.findall("(?=<td class=\"gsc_a_t\">).*?(?=</span>)", hits)
authors_ = [re.search('(?<=<div class=\"gs_gray\">).*?(?=</div>)', x).group(0) for x in publications]
titles = [re.search('(?<=class=\"gsc_a_at\">).*?(?=</a>)', x).group(0) for x in publications]
years = [re.search('20[0-9][0-9]', x).group(0) for x in publications]
citation_links = ['https://scholar.google.com/citations?view_op=view_citation&' + re.search('(?=citation_for_view).*?(?=" )', x).group(0) for x in publications]


# In[8]:


authors = []
dates = []
journals = []
links = []
for citation_link in tqdm(citation_links):
    sp.run(f"wget '{citation_link}' -O tmp.html", shell=True)
    with open("tmp.html", 'rb') as infile:
        lines = infile.read().decode('unicode-escape')
        author_list, date, journal, *_ = re.findall('(?<=gsc_oci_value">).*?(?=</div>)', lines)
        if '"' in journal:
            journal = ''
        link = re.search('(?<=class="gsc_oci_title_link" href=").*?(?=")', lines).group(0)
        authors.append(BeautifulSoup(author_list).text)
        dates.append(BeautifulSoup(date).text)
        journals.append(journal)
        links.append(link)
        
#     time.sleep(5)
    sp.run("rm tmp.html", shell=True)


# In[9]:


title_length_limit = 75
abbreviated_titles = [title if len(title) < title_length_limit else title[:title_length_limit-3]+'...' for title in titles]


# In[34]:


vineet_led = [x.endswith('Bafna') and not x.startswith('Joseph Califano') for x in authors]


# In[41]:


paper_list = []
for title, author_list, link, journal, year, bafna_project in zip(abbreviated_titles, authors_, links, journals, years, vineet_led):
    if not bafna_project:
        continue
    paper_list.append('\t\t\t' + f"""<li><div class=link>
\t\t\t\t<a href=\"{link}\">{title}</a>
\t\t\t\t<br>
\t\t\t\t<span>{author_list}</span>
\t\t\t\t<br>
\t\t\t\t<span>{journal}, {year}</span>
\t\t\t\t</li>
""".strip())
paper_list = '\n'.join(paper_list)


# In[42]:


with open('index.html') as infile:
    lines = infile.read()
    start_papers = lines.index('<ul>') + len('<ul>\n')
    end_papers = lines.index('</ul>') - len('\n\t\t')

with open('index.html', 'w') as outfile:
    outfile.write(lines[:start_papers] + paper_list + lines[end_papers:])


# In[ ]:


sp.run(f"cd '{os.getcwd()}'; git add .; git commit -m 'Automated Website Update'; git push origin main", shell=True)


# In[ ]:




