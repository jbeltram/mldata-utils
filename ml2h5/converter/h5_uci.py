import os, numpy
from basehandler import BaseHandler


class H5_UCI(BaseHandler):
    """Handle UCI files."""

    def _get_comment(self):
        try:
            name = '.'.join(self.fname.split('.')[:-1])
            if not name:
                name = '.'.join(self.fname.split('-')[:-1])

            if os.path.exists(name + '.names'):
                fp = open(name + '.names', 'r')
            elif os.path.exists(name + '.info'):
                fp = open(name + '.info', 'r')
            else:
                return ''

            comment = ''.join(fp.readlines())
            fp.close()
            return comment
        except ValueError:
            return ''
        except IOError:
            return ''


    def _ignore_line(self, line):
        line = line.strip()
        if not line:
            return True
        if line.startswith(';;;'):
            return True

        return False


    def _parse(self):
        fp = open(self.fname, 'r')
        lineno = 0
        num_items = None
        data = []

        for line in fp:
            lineno += 1

            if self._ignore_line(line):
                continue

            if not self.seperator:
                items = line.strip().split()
            else:
                items = line.strip().split(self.seperator)
            if not num_items: # do some init
                num_items = len(items)
                for i in xrange(num_items):
                    data.append([])

            for i in xrange(len(items)):
                item = items[i].strip()
                if not item:
                    continue

                try:
                    if item == '?': # missing value
                        item = numpy.nan
                    data[i].append(item)
                except IndexError:
                    self.warn('Index Error in line ' + str(lineno) + ', column ' + str(i))

        fp.close()
        return data


    def read(self):
        ordering = []
        predata = self._parse()
        data = {}

        for i in xrange(len(predata)):
            arr = numpy.array(predata[i])

            # everything is nan -> keep as str
            try:
                all_is_nan = numpy.isnan(arr).all()
            except AttributeError:
                all_is_nan = False

            if all_is_nan:
                arr = arr.astype(self.str_type)
                name = 'str' + str(i)
            else:
                try:
                    arr = arr.astype(numpy.int)
                    name = 'int' + str(i)
                except ValueError:
                    try:
                        arr = arr.astype(numpy.double)
                        name = 'double' + str(i)
                    except ValueError: # fallback to str
                        arr = arr.astype(self.str_type)
                        name = 'str' + str(i)

            data[name] = arr
            ordering.append(name)

        return {
            'name': self.get_name(),
            'comment': self._get_comment(),
            'ordering':ordering,
            'names':ordering,
            'data':data,
        }
