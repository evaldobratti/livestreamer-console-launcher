class Menu(object):
	def __init__(self, options, page=0, previous=None):
		self.options = options
		self.itens_per_page = 8
		self.current_page = page
		self.previous = previous

		start_index = self.current_page * self.itens_per_page
		final_index = start_index + self.itens_per_page
		self.current_options = self.options[start_index:final_index]

		if len(self.options) > self.itens_per_page:
			self.current_options.append(NextPage(self))

		if self.current_page > 0:
			self.current_options.append(PreviousPage(self))

		if self.previous:
			self.current_options.append(Return(self.previous))
	
	def show_options(self):
		self.current_options.append(Exit(None))

		for i, option in enumerate(self.current_options):
			print str(i) + ' - ' + option.format()

	def interprete(self, option):
		return self.current_options[option].advance(self)


class MenuAction(object):
	
	def __init__(self, option=None):
		self.option = option

	def advance(self, actual_menu):
		pass

	def format(self):
		return str(self.option)


class NextPage(MenuAction):
	def advance(self, actual_menu):
		return Menu(self.option.options, self.option.current_page + 1, previous=self.option.previous)

	def format(self):
		return 'Next page'


class PreviousPage(MenuAction):
	def advance(self, actual_menu):
		return Menu(self.option.options, self.option.current_page - 1, previous=self.option.previous)

	def format(self):
		return 'Previous page'


class Return(MenuAction):
	def advance(self, actual_menu):
		return Menu(self.option.options, previous=self.option.previous)

	def format(self):
		return 'Return to previous menu'


class Exit(MenuAction):
	def advance(self, actual_menu):
		return None

	def format(self):
		return 'Exit'