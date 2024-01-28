from bs4 import BeautifulSoup

import analyzer
import css


class ListFilesTask(analyzer.Task):
    def run(self, context, report):
        context.set_property('html_files', [item for item in context.project_dir.glob('*.html') if item.is_file()])
        context.set_property('css_files', [item for item in context.project_dir.glob('*.css') if item.is_file()])


class ProjetNameTask(analyzer.Task):
    def run(self, context, report):
        report.append(context.project_name)


class CountHTMLFilesTask(analyzer.Task):
    def run(self, context, report):
        html_file_count = len(context.get_property('html_files'))
        report.append(html_file_count)
        return html_file_count



class CountCSSFilesTask(analyzer.Task):
    def run(self, context, report):
        report.append(len(context.get_property('css_files')))


class ExtractAuthorsTask(analyzer.Task):
    def run(self, context, report):
        authors = []

        for html_file in context.get_property('html_files'):
            soup = BeautifulSoup(html_file.read_text(), 'html.parser')

            author_meta = soup.find('meta', attrs={'name': 'author'})
            author = author_meta['content'].lower() if author_meta else None

            if author and 'robert cailliau' not in author not in authors:
                authors.append(author)

        report.append('|'.join(authors))


class HyperlinkScoreTask(analyzer.Task):
    def run(self, context, report):
        pages = []
        urls = []
        score = 0

        for html_file in context.get_property('html_files'):
            pages.append(html_file.name.lower())

            soup = BeautifulSoup(html_file.read_text(), 'html.parser')
            for tag in soup.find_all('a'):
                if tag.get('href'):
                    urls.append(tag.get('href').strip())

        # Remove external urls
        local_urls = [url for url in urls if not url.startswith('http')]
        if len(local_urls) != len(urls):
            score += 2

        # cleanup
        local_urls = [url.lower() for url in local_urls if not url.startswith('data') and not url.startswith('.')]
        local_urls_count = len(local_urls)

        # Check if urls starting with file://
        local_urls = [url for url in local_urls if not url.startswith('file://')]
        if len(local_urls) == local_urls_count:
            score += 1

        # Check if url to all pages
        unknown_pages = [url for url in local_urls if url not in pages]
        unlinked_pages = [page for page in pages if page not in local_urls]
        if len(unknown_pages) == 0 and len(unlinked_pages) == 0:
            score += 2

        report.append(score / 5)


class CheckIndexTask(analyzer.Task):
    def run(self, context, report):
        output = 1 if 'index.html' in [file.name.lower() for file in context.get_property('html_files')] else 0
        report.append(output)


class ImageScoreTask(analyzer.Task):
    def run(self, context, report):
        page_count = len(context.get_property('html_files'))
        images = []

        score = 0

        for html_file in context.get_property('html_files'):
            soup = BeautifulSoup(html_file.read_text(), 'html.parser')

            # check img tag
            for img in soup.find_all('img'):
                images.append(img.get('src').strip())

        # check for image with bad path
        bad_src = [image for image in images if '\\' in image or image == '']
        if len(bad_src) == 0:
            score += 1

        # cleanup images
        images = [image for image in images if image != '']

        # count images
        image_count = len(images)
        if image_count >= page_count:
            score += 2
        elif image_count == 1:
            score += 1

        report.append(score / 3)


class HTMLScoreTask(analyzer.Task):
    def run(self, context, report):
        page_count = len(context.get_property('html_files'))
        titles = []
        h1_tags = []
        page_without_paragraphe_count = 0
        score = 0

        for html_file in context.get_property('html_files'):
            soup = BeautifulSoup(html_file.read_text(), 'html.parser')

            excluded_titles = ["Titre dans l'onglet du navigateur", "Titre d'une page secondaire"]
            titles = [title.getText() for title in soup.find_all('title')]
            titles = [title for title in titles if title not in excluded_titles]

            h1_tags = [title.getText() for title in soup.find_all('h1')]
            h1_tags = [text for text in h1_tags if text not in excluded_titles]

            if len(soup.find_all('p')) == 0:
                page_without_paragraphe_count += 1

        print(context.pupil_dir, page_without_paragraphe_count)

        title_count = len(titles)
        if title_count == page_count:
            score += 2
        elif title_count == 1:
            score += 1

        h1_count = len(h1_tags)
        if h1_count == page_count:
            score += 2
        elif h1_count == 1:
            score += 1

        page_without_paragraphe_ratio = page_without_paragraphe_count * 100 / page_count
        if page_without_paragraphe_ratio < 50:
            score += 1

        report.append(score / 5)


class CSSScoreTask(analyzer.Task):
    def run(self, context, report):
        score = 0

        selectors = []
        already_exists = ['h2', '.texte-mis-en-forme-exemple', '.titre-page-exemple', '.petite-image-exemple', 'table',
                          'td']

        for css_file in context.get_property('css_files'):
            selectors += css.get_selectors(css_file.read_text())
        selectors = [item for item in selectors if item not in already_exists]
        type_selectors = [item for item in selectors if not item.startswith('.')]
        class_selectors = [item for item in selectors if item.startswith('.')]

        if len(type_selectors) > 0:
            score += 1

        if len(class_selectors) > 0:
            score += 2

        if len(selectors) >= 4:
            score += 2

        report.append(score / 5)
