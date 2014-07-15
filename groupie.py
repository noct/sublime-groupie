import sublime, sublime_plugin

from operator import methodcaller
from os.path import basename
from fnmatch import fnmatch

def move_to_end(view, group):
	win = view.window()
	win.set_view_index(view, group, len(win.views_in_group(group)))

class GroupieCommand(sublime_plugin.WindowCommand):

	def sort_group(self, group):
		win = self.window
		views = sorted(win.views_in_group(group), key=lambda v: basename(v.file_name()))

		for i in range(len(views)):
			view = views[i]
			win.set_view_index(view, group, i)

	def load_settings(self):
		self.settings = sublime.load_settings("groupie.sublime-settings")

	def run(self):
		self.load_settings()

		win = self.window
		default_group = self.settings.get("default_group", 0)
		rules = self.settings.get("rules", [])
		num_groups = win.num_groups()
		cur_view = win.active_view()
		temp_view = {}

		for cur_group in range(num_groups):
			if cur_group != default_group:
				win.focus_group(cur_group)
				temp_view[cur_group] = win.new_file()
				for view in win.views_in_group(cur_group):
					move_to_end(view, default_group)

		for rule in rules:
			dest_group = rule["index"]
			patterns = rule["match"]
			if dest_group != default_group:
				for view in win.views_in_group(default_group):
					file_name = view.file_name()
					if view.file_name():
						for pattern in patterns:
							if fnmatch(file_name, pattern):
								move_to_end(view, dest_group)

		for cur_group in range(num_groups):
			if cur_group != default_group:
				print("closing")
				win.focus_view(temp_view[cur_group])
				win.run_command("close_file")

		if self.settings.get("sort", False):
			for i in range(num_groups):
				self.sort_group(i)

		win.focus_view(cur_view)

# ST3 features a plugin_loaded hook which is called when ST's API is ready.
#
# We must therefore call our init callback manually on ST2. It must be the last
# thing in this plugin (thanks, beloved contributors!).
if not int(sublime.version()) > 3000:
	plugin_loaded()
