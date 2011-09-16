from theses import *

if __name__ == '__main__':
    spider = ThesisSpider()
    print 'Showing all areas that have at least 100 thesis:'
    areas = []
    n = 0
    for i in range(50):
        for a in spider.areas(min_thesis=100, page=i):
            areas.append(a)
            print '\t', a['name'], a['size']
            n += a['size']

    print 'Total: %d areas, %d theses' % (len(areas), n)
