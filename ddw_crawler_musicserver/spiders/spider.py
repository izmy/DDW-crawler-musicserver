import scrapy
 
class MSSpider(scrapy.Spider):
    name = 'MSSpider'
    user_agent = 'DDW'
    download_delay = 1.0
    start_urls = ['http://musicserver.cz/']

    def parse(self, response):
        for title in response.css('.clanek'):
            articleUrl = title.css('.nadpis ::attr(href)').extract_first()
            score = title.css('div:first-child b ::text').extract_first()
            request = scrapy.Request(response.urljoin(articleUrl), callback=self.parseArticle)
            request.meta['item'] = {}
            if score:
                request.meta['item'].update({
                    'score': title.css('div:first-child b ::text').extract_first()
                })
            yield request
        
        next_page = response.css('#paging .next ::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parseArticle(self, response):
        item = response.meta['item']
        base = response.css('.stred')
        headline = base.css('h1 ::text').extract_first()
        title = response.css('.stred').xpath("img/@alt").extract_first()
        perex = base.css('.perex ::text').extract_first()
        category = base.css('div:first-of-type a ::text').extract()[0]
        author = base.css('div:first-of-type a ::text').extract()[1]
        dateText = base.css('.stred div:first-of-type ::text').extract_first()
        date = dateText[8:-10]

        item.update({
            'headline': headline,
            'title': title,
            'date': date,
            'category': category,
            'author': author,
            'url': response.url
        })

        if perex:
            item.update({
                'perex': perex
            })

        if category == u"Recenze":
            review = base.css('.cd-box h2 ::text').extract_first() 
            released = base.css('.cd-box .notes').xpath('strong/following-sibling::text()[1]').extract_first().strip()
            length = base.css('.cd-box .notes').xpath('strong/following-sibling::text()[3]').extract_first().strip()
            label = base.css('.cd-box p:nth-of-type(3) a ::text').extract_first()
            tracklist = base.css('.cd-box .track-list').xpath('strong/following-sibling::text()[1]').extract_first().strip()
            item.update({
                'albumDetail': {
                    'artist': review.split(" - ")[0],
                    'album': review.split(" - ")[1],
                    'released': released,
                    'length': length,
                    'label': label,
                    'tracklist': tracklist,
                }
            })

        if (category == u"Na\u017eivo") or (category == u"Fotogalerie"):
            artist = base.css('.text div:first-child h2 ::text').extract_first()[5:].strip()
            live = response.css('.stred .text div:first-child p b ::text').extract()
            item.update({
                'liveDetail': {
                    'artist': artist,
                    'place': live[0],
                    'date': live[1],
                }
            })

        yield item
        
