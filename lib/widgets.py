# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import edit
import gtk

def define_widgets(self, gladefile):
	#widgets
	self.main_window = gladefile.get_widget('main_window')
	self.toolbar = gladefile.get_widget('toolbar1')
	# add movie window
	self.add_movie_window = gladefile.get_widget('add_movie')
	self.am_original_title = gladefile.get_widget('am_original_title')
	self.am_title = gladefile.get_widget('am_title')
	self.am_number = gladefile.get_widget('am_number')
	self.am_director = gladefile.get_widget('am_director')
	self.am_plot = gladefile.get_widget('am_plot')
	self.am_picture = gladefile.get_widget('am_image')
	self.am_picture_name = gladefile.get_widget('am_hide_image_name')
	self.am_year = gladefile.get_widget('am_year')
	self.am_runtime = gladefile.get_widget('am_runtime')
	self.am_with = gladefile.get_widget('am_with')
	self.am_country = gladefile.get_widget('am_country')
	self.am_genre = gladefile.get_widget('am_genre')
	self.am_media = gladefile.get_widget('am_media')
	self.am_classification = gladefile.get_widget('am_classification')
	self.am_studio = gladefile.get_widget('am_studio')
	self.am_site = gladefile.get_widget('am_site')
	self.am_imdb = gladefile.get_widget('am_imdb')
	self.am_trailer = gladefile.get_widget('am_trailer')
	self.am_discs = gladefile.get_widget('am_discs')
	self.am_source = gladefile.get_widget('am_source')
	self.am_obs = gladefile.get_widget('am_obs')
	self.am_plugin_desc = gladefile.get_widget('am_plugin_desc')
	self.am_plugin_image = gladefile.get_widget('am_plugin_image')
	# main treeview
	self.main_treeview = gladefile.get_widget('main_treeview')
	self.confirm_delete = gladefile.get_widget('confirm_delete')
	# main notebook
	self.e_number = gladefile.get_widget('e_number')
	self.e_original_title = gladefile.get_widget('e_original_title')
	self.e_title = gladefile.get_widget('e_title')
	self.e_director = gladefile.get_widget('e_director')
	self.e_plot = gladefile.get_widget('e_plot')
	self.e_picture = gladefile.get_widget('e_picture_image')
	self.e_picture_button = gladefile.get_widget('e_picture')
	self.e_year = gladefile.get_widget('e_year')
	self.e_runtime = gladefile.get_widget('e_runtime')
	self.e_with = gladefile.get_widget('e_with')
	self.e_country = gladefile.get_widget('e_country')
	self.e_genre = gladefile.get_widget('e_genre')
	self.e_media = gladefile.get_widget('e_media')
	self.e_classification = gladefile.get_widget('e_classification')
	self.e_studio = gladefile.get_widget('e_studio')
	self.e_site = gladefile.get_widget('e_site')
	self.e_imdb = gladefile.get_widget('e_imdb')
	self.e_trailer = gladefile.get_widget('e_trailer')
	self.e_discs = gladefile.get_widget('e_discs')
	self.e_obs = gladefile.get_widget('e_obs')
	self.loan_info = gladefile.get_widget('loan_information')
	# volumes/collections tab
	self.e_volume_combo = gladefile.get_widget('e_volume_combo')
	self.e_collection_combo = gladefile.get_widget('e_collection_combo')
	self.e_volume_id = gladefile.get_widget('e_volume_id')
	self.e_collection_id = gladefile.get_widget('e_collection_id')
	self.show_volume_entries_button = gladefile.get_widget('show_volume_entries_button')
	self.show_collection_entries_button = gladefile.get_widget('show_collection_entries_button')
	# get from web
	self.b_get_from_web = gladefile.get_widget('get_from_web')
	self.c_web_source = gladefile.get_widget('combo_source')
	self.progressbar = gladefile.get_widget('w_progress')
	# results
	self.w_results = gladefile.get_widget('results')
	self.results_treeview = gladefile.get_widget('results_treeview')
	self.update_button = gladefile.get_widget('update_button')
	# statusbar
	self.statusbar = gladefile.get_widget('statusbar')
	# preferences
	self.w_preferences = gladefile.get_widget('w_preferences')	
	self.epdf_reader = gladefile.get_widget('pdf_reader_entry')
	# cover print
	self.w_print_cover_simple = gladefile.get_widget('w_print_cover_simple')
	self.w_print_cover_image = gladefile.get_widget('w_print_cover_image')
	self.cover_simple_size = gladefile.get_widget('cover_simple_size')
	self.cover_simple_include_movie_number = gladefile.get_widget('cover_simple_include_movie_number')
	self.cover_image_size = gladefile.get_widget('cover_image_size')
	self.cover_image_number = gladefile.get_widget('cover_image_number')
	self.cover_simple_include_poster = gladefile.get_widget('cover_simple_include_poster')
	#people
	self.w_people = gladefile.get_widget('w_people')
	self.ap_name = gladefile.get_widget('ap_name')
	self.ap_email = gladefile.get_widget('ap_email')
	self.ap_phone = gladefile.get_widget('ap_phone')
	self.ep_name = gladefile.get_widget('ep_name')
	self.ep_email = gladefile.get_widget('ep_email')
	self.ep_phone = gladefile.get_widget('ep_phone')
	self.ep_id = gladefile.get_widget('ep_id')
	self.p_treeview = gladefile.get_widget('p_treeview')
	#filter
	self.e_filter = gladefile.get_widget('filter_txt')
	self.filter_criteria = gladefile.get_widget('filter_criteria')
	self.w_add_person = gladefile.get_widget('w_add_person')
	self.w_edit_person = gladefile.get_widget('w_edit_person')
	#loan
	self.w_loan_to = gladefile.get_widget('w_loan_to')
	self.return_button = gladefile.get_widget('return_button')
	self.loan_button = gladefile.get_widget('loan_button')
	self.loan_to = gladefile.get_widget('loan_to')
	self.list_loaned = gladefile.get_widget('list_loaned_movies')
	#prefs
	self.view_image = gladefile.get_widget('view_image')
	self.view_otitle = gladefile.get_widget('view_otitle')
	self.view_title = gladefile.get_widget('view_title')
	self.view_director = gladefile.get_widget('view_director')
	self.p_media = gladefile.get_widget('p_media')
	self.p_color = gladefile.get_widget('p_color')
	self.p_condition = gladefile.get_widget('p_condition')
	self.p_region = gladefile.get_widget('p_region')
	self.p_layers = gladefile.get_widget('p_layers')
	#buttons
	self.go_site = gladefile.get_widget('go_site')
	self.go_imdb = gladefile.get_widget('go_imdb')
	self.go_trailer = gladefile.get_widget('go_trailer')
	self.new_db = gladefile.get_widget('new_bt')
	#notebooks
	self.nb_add = gladefile.get_widget('notebook_add')
	#ratings
	self.image_rating = gladefile.get_widget('image_rating')
	self.image_add_rating = gladefile.get_widget('image_add_rating')
	self.menu_toolbar = gladefile.get_widget('menu_toolbar')	
	self.export_menu = gladefile.get_widget('export_menu')
	
	self.rating_slider = gladefile.get_widget('rating_scale')
	self.rating_slider_add = gladefile.get_widget('rating_scale_add')
	
	#tech data
	self.e_condition = gladefile.get_widget('e_condition')
	self.e_color = gladefile.get_widget('e_color')
	self.e_region = gladefile.get_widget('e_region')
	self.e_layers = gladefile.get_widget('e_layers')
	
	self.am_condition = gladefile.get_widget('am_condition')
	self.am_color = gladefile.get_widget('am_color')
	self.am_region = gladefile.get_widget('am_region')
	self.am_layers = gladefile.get_widget('am_layers')
	
	#spellchecker
	self.spellchecker = gladefile.get_widget('spellchecker_pref')
	self.spell_notes = gladefile.get_widget('spell_notes')
	self.spell_plot = gladefile.get_widget('spell_plot')
	self.spell_lang = gladefile.get_widget('spell_lang')
	
	self.e_seen = gladefile.get_widget('e_seen')
	self.am_seen = gladefile.get_widget('am_seen')
	
	self.b_email_reminder = gladefile.get_widget('b_email_reminder')
	self.loan_history = gladefile.get_widget('loan_history')	
	self.default_plugin = gladefile.get_widget('default_plugin')
	
	self.rating_image = gladefile.get_widget('rating_image')
	
	self.mail_smtp_server = gladefile.get_widget('mail_smtp_server')
	self.mail_use_auth = gladefile.get_widget('mail_use_auth')
	self.mail_username = gladefile.get_widget('mail_username')
	self.mail_password = gladefile.get_widget('mail_password')
	self.mail_email = gladefile.get_widget('mail_email')
	
	self.all_movies = gladefile.get_widget('all_movies')
	
	# poster button related
	self.zoom_poster = gladefile.get_widget('zoom_poster')
	self.open_poster = gladefile.get_widget('open_poster')
	self.fetch_poster = gladefile.get_widget('fetch_poster')
	self.delete_poster = gladefile.get_widget('delete_poster')
	
	self.poster_window = gladefile.get_widget('poster_window')
	self.big_poster = gladefile.get_widget('big_poster')
	
	#main popup menu
	self.popup = gladefile.get_widget('popup')
	
	self.popup_loan = gladefile.get_widget('popup_loan')
	self.popup_return = gladefile.get_widget('popup_return')
	self.popup_email = gladefile.get_widget('popup_email')
	
	self.f_col = gladefile.get_widget('f_col')
	
	#add some tooltips
	self.tooltips = gtk.Tooltips()
	self.tooltips.set_tip(self.epdf_reader, _('Define here the PDF reader you want to use within Griffith. Popular choices are xpdf, gpdf, evince or kpdf. Make sure you have this program installed and working first.'))
	self.tooltips.set_tip(self.spell_lang, _("Here you can define the desired language to use while spell checking some fields. Use you locale setting. For example, to use european portuguese spell checking enter 'pt'"))
	self.tooltips.set_tip(self.mail_smtp_server, _("Use this entry to define the SMTP server you want to use to send e-mails. On *nix systems, 'localhost' should work. Alternatively, you can use your Internet Service Provider's SMTP server address."))
	self.tooltips.set_tip(self.mail_email, _("This is the from e-mail address that should be used to all outgoing e-mail. You want to include your own e-mail address here probably."))	
	
	
	# add handlers for windows delete events
	self.add_movie_window.connect("delete_event", self.on_delete_event_am)
	self.w_results.connect("delete_event", self.on_delete_event_r)
	self.w_people.connect("delete_event", self.on_delete_event_wp)
	self.w_add_person.connect("delete_event", self.on_delete_event_ap)
	self.w_edit_person.connect("delete_event", self.on_delete_event_ep)
	self.w_loan_to.connect("delete_event", self.on_delete_event_lt)
	self.w_print_cover_simple.connect("delete_event", self.on_delete_event_pcs)
	self.w_print_cover_image.connect("delete_event", self.on_delete_event_pci)
	self.w_preferences.connect("delete_event", self.on_delete_event_p)
	
	# poster events
	self.zoom_poster.connect("enter", self.z_poster)
	self.zoom_poster.connect("leave", self.z_poster_hide)
		 
	# define handlers for general events
		
	dic = {
		"gtk_main_quit"                         : self.destroy,
		"on_about1_activate"                    : self.about_dialog,
		"on_quit1_activate"                     : self.destroy,
		"on_toolbar_quit_clicked"               : self.destroy,
		"on_toolbar_add_clicked"                : self.add_movie,
		"on_cancel_add_movie_clicked"           : self.hide_add_movie,
		"on_add1_activate"                      : self.add_movie,
		"on_add_movie_clicked"                  : self.add_movie_db,
		"on_add_movie_close_clicked"            : self.add_movie_close_db,
		"on_delete_movie_clicked"               : self.delete_movie,
		"on_delete1_movie_activate"             : self.delete_movie,
		"on_ok_delete_clicked"                  : self.delete_movie_from_db,
		"on_main_treeview_row_activated"        : self.treeview_clicked,
		"on_row_activated"                      : self.treeview_clicked,
		"on_get_from_web_clicked"               : self.get_from_web,
		"on_results_cancel_clicked"             : self.hide_results,
		"on_results_select_clicked"             : self.populate_dialog_with_results,
		"on_update_button_clicked"              : self.update_movie,
		"on_preferences1_activate"              : self.show_preferences,
		"on_cancel_preferences_clicked"         : self.hide_preferences,
		"on_save_preferences_clicked"           : self.save_preferences,
		"on_backup_activate"                    : self.backup,
		"on_restore_activate"                   : self.restore,
		"on_cover_simple_activate"              : self.print_cover_simple_show,
		"on_cancel_print_cover_simple_clicked"  : self.print_cover_simple_hide,
		"on_b_print_cover_simple_clicked"       : self.print_cover_simple_process,
		"on_add_clear_clicked"                  : self.clear_add_dialog,
		"on_people_activate"                    : self.show_people_window,
		"on_cancel_people_clicked"              : self.hide_people_window,
		"on_filter_txt_changed"                 : self.filter_txt,
		"on_filter_criteria_changed"            : self.filter_txt,
		"on_clear_filter_clicked"               : self.clear_filter,
		"on_people_add_clicked"                 : self.add_person,
		"on_add_person_cancel_clicked"          : self.add_person_cancel,
		"on_add_person_db_clicked"              : self.add_person_db,
		"on_people_delete_clicked"              : self.delete_person,
		"on_people_edit_clicked"                : self.edit_person,
		"on_edit_person_cancel_clicked"         : self.edit_person_cancel,
		"on_update_person_clicked"              : self.update_person,
		"on_clone_activate"                     : self.clone_movie,
		"on_loan_button_clicked"                : self.loan_movie,
		"on_cancel_loan_clicked"                : self.cancel_loan,
		"on_loan_ok_clicked"                    : self.commit_loan,
		"on_return_button_clicked"              : self.return_loan,
		"on_list_loaned_movies_activate"        : self.filter_loaned,
		"on_cover_choose_image_activate"        : self.print_cover_image,
		"on_cancel_print_cover_image_clicked"   : self.print_cover_image_hide,
		"on_b_print_cover_image_clicked"        : self.print_cover_image_process,
		"on_go_site_clicked"                    : self.go_oficial_site,
		"on_combo_source_changed"               : self.source_changed,
		# poster
		"on_e_picture_clicked"                  : self.change_poster,
		"on_open_poster_clicked"                : self.change_poster,
		"on_delete_poster_clicked"              : self.del_poster,
		#"on_zoom_poster_clicked"               : self.z_poster,
		"on_fetch_poster_clicked"               : self.get_poster,
		"on_go_imdb_clicked"                    : self.go_imdb_site,
		"on_go_trailer_clicked"                 : self.go_trailer_site,
		"on_new_bt_clicked"                     : self.new_dbb,
		"on_new_activate"                       : self.new_dbb,
		"on_view_toolbar_activate"              : self.toggle_toolbar,
		"on_seen_movies_activate"               : self.filter_not_seen,
		"on_all_movies_activate"                : self.filter_all,
		"on_rating_scale_value_changed"         : self.scale_rating_change,
		"on_rating_scale_add_value_changed"     : self.scale_rating_change_add,
		"on_e_seen_released"                    : self.toggle_seen,
		"on_sugest_activate"                    : self.sugest_movie,
		"on_email_reminder_clicked"             : self.email_reminder,
		"on_go_first_clicked"                   : self.go_first,
		"on_go_last_clicked"                    : self.go_last,
		"on_popup_delete_activate"              : self.delete_movie,
		"on_popup_clone_activate"               : self.clone_movie,
		"on_popup_simple_activate"              : self.print_cover_simple_show,
		"on_popup_choose_image_activate"        : self.print_cover_image,
		"on_popup_loan_activate"                : self.loan_movie,
		"on_popup_return_activate"              : self.return_loan,
		"on_popup_email_activate"               : self.email_reminder,
		"on_e_add_volume_button_clicked"        : self.e_add_volume,
		"on_e_add_collection_button_clicked"    : self.e_add_collection,
		"on_e_remove_volume_button_clicked"     : self.e_remove_volume,
		"on_e_remove_collection_button_clicked" : self.e_remove_collection,
		"on_e_rename_volume_button_clicked"     : self.e_rename_volume,
		"on_e_rename_collection_button_clicked" : self.e_rename_collection,
		"on_e_show_volume_button_clicked"       : self.e_show_volume,
		"on_e_show_collection_button_clicked"   : self.e_show_collection,
		"on_f_col_changed"                      : self.filter_collection
	}
	gladefile.signal_autoconnect(dic)
