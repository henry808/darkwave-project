import pathlib
from bs4 import BeautifulSoup
import logging
import shutil

# Inject Google Analytics
def inject_ga(GA_ID, debug):

    # Note: Please replace the id from G-XXXXXXXXXX to whatever your
    # web application's id is. You will find this in your Google Analytics account

    GA_JS = f"""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);/}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
</script>
"""

    if debug:
        st.write(GA_JS)

    # Insert the script in the head tag of the static template inside your virtual env
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)

# Get Secret
# GA_TAG needs to go into the ENV as a secret.
try:
    GA_TAG = st.secrets["GA_TAG"]
except KeyError:
    if debug:
        st.write("Error: Could not find GA_TAG")
    GA_TAG = ""
if debug:
    st.write("Test: ", GA_TAG)

if GA_TAG:
    inject_ga(GA_TAG, debug)
