# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2006 Vasco Nunes
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
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

from gettext import gettext as _
import edit
import gtk
import sys

def define_widgets(self, gladefile):
	get = lambda x: gladefile.get_widget(x)
	self.widgets = {}
	
	self.widgets['window'] = get('main_window')
	self.widgets['window'].connect('key_press_event', self.on_key_press_event)
	self.widgets['treeview'] = get('main_treeview')
	self.widgets['treeview'].connect('button_press_event', self.on_maintree_button_press_event)
	self.widgets['statusbar'] = get('statusbar')
	self.widgets['progressbar']    = get('w_progress')	# get from web
	#buttons
	self.widgets['new_db']      = get('new_bt')
	self.widgets['toolbar'] = get('toolbar1')
	

	self.widgets['movie'] = {#{{{
		'cast':			get('m_cast'),
		'classification':	get('m_classification'),
		'collection':		get('m_collection'),
		'color':		get('m_color'),
		'condition':		get('m_condition'),
		'country':		get('m_country'),
		'director':		get('m_director'),
		'genre':		get('m_genre'),
		'imdb':			get('m_imdb'),
		'layers':		get('m_layers'),
		'loan_info':		get('loan_information'),
		'loaned_icon':		get('m_loaned_icon'),
		'medium':		get('m_medium'),
		'notes':		get('m_notes'),
		'number':		get('m_number'),
		'o_title':		get('m_o_title'),
		'picture':		get('m_picture_image'),
		'picture_button':	get('m_picture'),
		'plot':			get('m_plot'),
		'region':		get('m_region'),
		'runtime':		get('m_runtime'),
		'seen_icon':		get('m_seen_icon'),
		'site':			get('m_site'),
		'studio':		get('m_studio'),
		'tags':			get('m_tags'),
		'title':		get('m_title'),
		'trailer':		get('m_trailer'),
		'vcodec':		get('m_vcodec'),
		'volume':		get('m_volume'),
		'year':			get('m_year'),
		'audio_vbox':		get('m_audio_vbox'),
		'subtitle_vbox':	get('m_subtitle_vbox'),
		'show_collection_button':get('m_show_collection_button'),
		'show_volume_button':	get('m_show_volume_button'),
		'go_o_site_button':	get('go_o_site'),
		'go_site_button':	get('go_site'),
		'go_trailer_button':	get('go_trailer'),
		'return_button':	get('return_button'),
		'loan_button':		get('loan_button'),
		'loan_history':		get('loan_history'),
		'loan_to':		get('loan_to'),
		'email_reminder_button':get('b_email_reminder'),
		'image_rating':		get('m_image_rating'),
	}
	#}}}

	self.widgets['add'] = {#{{{
		'window':	get('add_movie'),
		'notebook':	get('notebook_add'),
		'classification':get('am_classification'),
		'collection':	get('am_collection_combo'),
		'color':	get('am_color'),
		'condition':	get('am_condition'),
		'country':	get('am_country'),
		'director':	get('am_director'),
		'discs':	get('am_discs'),
		'genre':	get('am_genre'),
		'site':		get('am_imdb'),
		'layers':	get('am_layers'),
		'media':	get('am_media'),
		'medium_vbox':	get('am_medium_vbox'),
		'number':	get('am_number'),
		'notes':	get('am_obs'),
		'o_title':	get('am_original_title'),
		'picture':	get('am_image'),
		'picture_name':	get('am_hide_image_name'),
		'plot':		get('am_plot'),
		'plugin_desc':	get('am_plugin_desc'),
		'plugin_image':	get('am_plugin_image'),
		'region':	get('am_region'),
		'runtime':	get('am_runtime'),
		'seen':		get('am_seen'),
		'o_site':	get('am_site'),
		'source':	get('am_source'),
		'studio':	get('am_studio'),
		'tag_vbox':	get('am_tag_vbox'),
		'title':	get('am_title'),
		'trailer':	get('am_trailer'),
		'vcodec':	get('am_vcodec'),
		'volume':	get('am_volume_combo'),
		'cast':		get('am_with'),
		'year':		get('am_year'),
		'image_rating': get('image_add_rating'),
		'rating_slider':get('rating_scale_add'),
		'lang_menu':	get('lang_menu'),
		'lang_treeview':get('lang_treeview'),
		'b_get_from_web':get('get_from_web'),
		'c_web_source':	get('combo_source'), # c_web_source
		'delete_poster': get('delete_poster'),
		'add_button':	get('am_add_button'),
		'add_close_button':get('am_add_close_button'),
		'clear_button':	get('am_clear_button'),
		'save_button':	get('am_save_button'),
	}
	self.widgets['add']['window'].connect('delete_event', self.on_delete_event_am)
	self.widgets['add']['lang_treeview'].connect('button_press_event', self.on_lang_treeview_button_press_event)
	#}}}

	self.widgets['preferences'] = {#{{{
		'window':		get('w_preferences'),
		'treeview':		get('p_treeview'),
		'color':		get('p_color'),
		'condition':		get('p_condition'),
		'db_details':		get('p_db_details'),
		'db_host':		get('p_db_host'),
		'db_name':		get('p_db_name'),
		'db_passwd':		get('p_db_passwd'),
		'db_port':		get('p_db_port'),
		'db_type':		get('p_db_type'),
		'db_user':		get('p_db_user'),
		'epdf_reader':		get('pdf_reader_entry'),
		'font':			get('p_font'),
		'layers':		get('p_layers'),
		'media':		get('p_media'),
		'region':		get('p_region'),
		's_classification':	get('p_s_classification'),
		's_country':		get('p_s_country'),
		's_director':		get('p_s_director'),
		's_genre':		get('p_s_genre'),
		's_image':		get('p_s_image'),
		's_notes':		get('p_s_notes'),
		's_o_site':		get('p_s_o_site'),
		's_o_title':		get('p_s_o_title'),
		's_plot':		get('p_s_plot'),
		's_rating':		get('p_s_rating'),
		's_runtime':		get('p_s_runtime'),
		's_site':		get('p_s_site'),
		's_studio':		get('p_s_studio'),
		's_title':		get('p_s_title'),
		's_trailer':		get('p_s_trailer'),
		's_cast':		get('p_s_cast'),
		's_year':		get('p_s_year'),
		'vcodec':		get('p_vcodec'),
		'view_image':		get('view_image'),
		'view_o_title':		get('view_otitle'),
		'view_title':		get('view_title'),
		'view_director':	get('view_director'),
		'rating_image':		get('rating_image'),
		'spellchecker':		get('spellchecker_pref'),
		'spell_notes':		get('spell_notes'),
		'spell_plot':		get('spell_plot'),
		'spell_lang':		get('spell_lang'),
		'default_plugin':	get('default_plugin'),
		'mail_smtp_server':	get('mail_smtp_server'),
		'mail_use_auth':	get('mail_use_auth'),
		'mail_username':	get('mail_username'),
		'mail_password':	get('mail_password'),
		'mail_email':		get('mail_email'),
		'lang_name':		get('lang_name_combo'),
		'tag_name':		get('tag_name_combo'),
		'acodec_name':		get('acodec_name_combo'),
		'achannel_name':	get('achannel_name_combo'),
		'subformat_name':	get('subformat_name_combo'),
		'medium_name':		get('medium_name_combo'),
		'vcodec_name':		get('vcodec_name_combo'),
		'sortby':		get('p_sortby'),
		'sortby_reverse':	get('p_sortby_reverse'),
	}
	self.widgets['preferences']['treeview'].connect('button_press_event', self.on_p_tree_button_press_event)
	self.widgets['preferences']['window'].connect('delete_event', self.on_delete_event_p)
	#}}}

	self.widgets['results'] = {#{{{
		'window':	get('results'),
		'treeview':	get('results_treeview'),
		'select':	get('results_select'),
		'cancel':	get('results_cancel'),
	}
	self.widgets['results']['window'].connect('delete_event', self.on_delete_event_r)
	#}}}

	self.widgets['print_cover'] = {#{{{
		# TODO: merge these two windows
		'window_simple':	get('w_print_cover_simple'),
		'window_image':		get('w_print_cover_image'),
		'cs_size':		get('cover_simple_size'),
		'cs_include_movie_number':get('cover_simple_include_movie_number'),
		'cs_include_poster':	get('cover_simple_include_poster'),
		'ci_size':		get('cover_image_size'),
		'ci_number':		get('cover_image_number'),
	}
	self.widgets['print_cover']['window_simple'].connect('delete_event', self.on_delete_event_pcs)
	self.widgets['print_cover']['window_image'].connect('delete_event', self.on_delete_event_pci)
	#}}}
	
	self.widgets['people'] = {#{{{
		'window':	get('w_people'),
		'treeview':	get('p_treeview'),
	}
	self.widgets['people']['window'].connect('delete_event', self.on_delete_event_wp)
	#}}}
	
	self.widgets['person'] = {#{{{
		# TODO: merge these two windows
		'window':	get('w_add_person'),
		'e_window':	get('w_edit_person'),
		'name':		get('ap_name'),
		'email':	get('ap_email'),
		'phone':	get('ap_phone'),
		'e_name':	get('ep_name'),
		'e_email':	get('ep_email'),
		'e_phone':	get('ep_phone'),
		'e_id':		get('ep_id'),
	}
	self.widgets['person']['window'].connect('delete_event', self.on_delete_event_ap)
	self.widgets['person']['e_window'].connect('delete_event', self.on_delete_event_ep)
	#}}}

	self.widgets['filter'] = {#{{{
		'text':		get('filter_txt'),
		'criteria':	get('filter_criteria'),
		'column':	get('f_col'),
	}#}}}
	
	self.widgets['menu'] = {#{{{
		'toolbar':	get('menu_toolbar'),
		'export':	get('export_menu'),
		'seen_movies':	get('seen_movies'),
		'loaned_movies':get('loaned_movies'),
		'all_movies':	get('all_movies'),
		'delete_poster': get('t_delete_poster'),
	}#}}}
	
	self.widgets['popups'] = {#{{{
		'main':		get('popup'),
		'loan':		get('popup_loan'),
		'return':	get('popup_return'),
		'email':	get('popup_email'),
	}#}}}
	
	self.widgets['w_loan_to']     = get('w_loan_to')
	self.widgets['w_loan_to'].connect('delete_event', self.on_delete_event_lt)

	self.widgets['poster_window'] = get('poster_window')
	self.widgets['poster_window'].connect('delete_event', self.on_delete_event_pw)
	self.widgets['big_poster']    = get('big_poster')

	#add some tooltips
	self.widgets['tooltips'] = gtk.Tooltips()
	self.widgets['tooltips'].set_tip(self.widgets['preferences']['epdf_reader'], _('Define here the PDF reader you want to use within Griffith. Popular choices are xpdf, gpdf, evince or kpdf. Make sure you have this program installed and working first.'))
	self.widgets['tooltips'].set_tip(self.widgets['preferences']['spell_lang'], _("Here you can define the desired language to use while spell checking some fields. Use you locale setting. For example, to use european portuguese spell checking enter 'pt'"))
	self.widgets['tooltips'].set_tip(self.widgets['preferences']['mail_smtp_server'], _("Use this entry to define the SMTP server you want to use to send e-mails. On *nix systems, 'localhost' should work. Alternatively, you can use your Internet Service Provider's SMTP server address."))
	self.widgets['tooltips'].set_tip(self.widgets['preferences']['mail_email'], _("This is the from e-mail address that should be used to all outgoing e-mail. You want to include your own e-mail address here probably."))

	# define handlers for general events
	gladefile.signal_autoconnect({#{{{
		'gtk_main_quit'                         : self.destroy,
		'on_about1_activate'                    : self.about_dialog,
		'on_quit1_activate'                     : self.destroy,
		'on_toolbar_quit_clicked'               : self.destroy,
		'on_toolbar_add_clicked'                : self.add_movie,
		'on_cancel_add_movie_clicked'           : self.hide_add_window,
		'on_add1_activate'                      : self.add_movie,
		'on_add_movie_clicked'                  : self.add_movie_db,
		'on_add_movie_close_clicked'            : self.add_movie_close_db,
		'on_delete_movie_clicked'               : self.delete_movie,
		'on_delete1_movie_activate'             : self.delete_movie,
		'on_main_treeview_row_activated'        : self.treeview_clicked,
		'on_row_activated'                      : self.treeview_clicked,
		'on_get_from_web_clicked'               : self.get_from_web,
		'on_update_button_clicked'              : self.update_movie,
		# preferences
		'on_preferences1_activate'              : self.show_preferences,
		'on_cancel_preferences_clicked'         : self.hide_preferences,
		'on_save_preferences_clicked'           : self.save_preferences,
		'on_p_db_type_changed'                  : self.on_p_db_type_changed,
		'on_backup_activate'                    : self.backup,
		'on_restore_activate'                   : self.restore,
		'on_merge_activate'                     : self.merge,
		'on_cover_simple_activate'              : self.print_cover_simple_show,
		'on_cancel_print_cover_simple_clicked'  : self.print_cover_simple_hide,
		'on_b_print_cover_simple_clicked'       : self.print_cover_simple_process,
		'on_add_clear_clicked'                  : self.clear_add_dialog,
		'on_am_save_button_clicked'             : self.update_movie,
		'on_people_activate'                    : self.show_people_window,
		'on_cancel_people_clicked'              : self.hide_people_window,
		'on_filter_txt_changed'                 : self.filter_txt,
		'on_filter_criteria_changed'            : self.filter_txt,
		'on_clear_filter_clicked'               : self.clear_filter,
		'on_people_add_clicked'                 : self.add_person,
		'on_add_person_cancel_clicked'          : self.add_person_cancel,
		'on_add_person_db_clicked'              : self.add_person_db,
		'on_people_delete_clicked'              : self.delete_person,
		'on_people_edit_clicked'                : self.edit_person,
		'on_edit_person_cancel_clicked'         : self.edit_person_cancel,
		'on_update_person_clicked'              : self.update_person,
		'on_clone_activate'                     : self.clone_movie,
		'on_loan_button_clicked'                : self.loan_movie,
		'on_cancel_loan_clicked'                : self.cancel_loan,
		'on_loan_ok_clicked'                    : self.commit_loan,
		'on_return_button_clicked'              : self.return_loan,
		'on_list_loaned_movies_activate'        : self.filter_loaned,
		'on_cover_choose_image_activate'        : self.print_cover_image,
		'on_cancel_print_cover_image_clicked'   : self.print_cover_image_hide,
		'on_b_print_cover_image_clicked'        : self.print_cover_image_process,
		'on_combo_source_changed'               : self.source_changed,
		# toolbar
		'on_view_toolbar_activate'              : self.toggle_toolbar,
		'on_go_first_clicked'                   : self.go_first,
		'on_go_last_clicked'                    : self.go_last,
		'on_go_back_clicked'                    : self.go_prev,
		'on_go_forward_clicked'                 : self.go_next,
		'on_new_bt_clicked'                     : self.new_dbb,
		'on_new_activate'                       : self.new_dbb,
		'on_edit_button_clicked'		: self.edit_movie,
		# poster
		'on_e_picture_clicked'                  : self.change_poster,
		'on_open_poster_clicked'                : self.change_poster,
		'on_zoom_poster_clicked'                : self.z_poster,
		'on_delete_poster_clicked'              : self.del_poster,
		'on_fetch_poster_clicked'               : self.get_poster,
		# URLs
		'on_goto_homepage_activate'             : self.on_goto_homepage_activate,
		'on_goto_forum_activate'                : self.on_goto_forum_activate,
		'on_goto_report_bug_activate'           : self.on_goto_report_bug_activate,
		'on_go_o_site_clicked'                  : self.go_oficial_site,
		'on_go_site_clicked'                    : self.go_site,
		'on_go_trailer_clicked'                 : self.go_trailer_site,
		'on_seen_movies_activate'               : self.filter_not_seen,
		'on_all_movies_activate'                : self.filter_all,
		'on_rating_scale_add_value_changed'     : self.scale_rating_change_add,
		'on_sugest_activate'                    : self.sugest_movie,
		'on_popup_delete_activate'              : self.delete_movie,
		'on_popup_clone_activate'               : self.clone_movie,
		'on_popup_simple_activate'              : self.print_cover_simple_show,
		'on_popup_choose_image_activate'        : self.print_cover_image,
		# loans
		'on_popup_loan_activate'                : self.loan_movie,
		'on_popup_return_activate'              : self.return_loan,
		'on_popup_email_activate'               : self.email_reminder,
		'on_email_reminder_clicked'             : self.email_reminder,
		# volumes/collections
		'on_am_collection_combo_changed'        : self.on_am_collection_combo_changed,
		'on_am_volume_combo_changed'            : self.on_am_volume_combo_changed,
		'on_am_add_volume_button_clicked'       : self.add_volume,
		'on_am_add_collection_button_clicked'   : self.add_collection,
		'on_am_remove_volume_button_clicked'    : self.remove_volume,
		'on_am_remove_collection_button_clicked': self.remove_collection,
		'on_f_col_changed'                      : self.filter_collection,
		'on_results_cancel_clicked'		: self.results_cancel_ck,
		# languages
		'on_lang_add_clicked'			: self.on_lang_add_clicked,
		'on_lang_remove_clicked'		: self.on_lang_remove_clicked,
		'on_am_lang_add_clicked'		: self.on_am_lang_add_clicked,
		'on_am_lang_remove_clicked'		: self.on_am_lang_remove_clicked,
		'on_lang_rename_clicked'		: self.on_lang_rename_clicked,
		'on_lang_name_combo_changed'		: self.on_lang_name_combo_changed,
		# tags
		'on_tag_add_clicked'			: self.on_tag_add_clicked,
		'on_tag_remove_clicked'			: self.on_tag_remove_clicked,
		'on_tag_rename_clicked'			: self.on_tag_rename_clicked,
		'on_tag_name_combo_changed'		: self.on_tag_name_combo_changed,
		# audio codecs
		'on_acodec_add_clicked'			: self.on_acodec_add_clicked,
		'on_acodec_remove_clicked'		: self.on_acodec_remove_clicked,
		'on_acodec_rename_clicked'		: self.on_acodec_rename_clicked,
		'on_acodec_name_combo_changed'		: self.on_acodec_name_combo_changed,
		# audio channels
		'on_achannel_add_clicked'		: self.on_achannel_add_clicked,
		'on_achannel_remove_clicked'		: self.on_achannel_remove_clicked,
		'on_achannel_rename_clicked'		: self.on_achannel_rename_clicked,
		'on_achannel_name_combo_changed'	: self.on_achannel_name_combo_changed,
		# subtitle formats
		'on_subformat_add_clicked'		: self.on_subformat_add_clicked,
		'on_subformat_remove_clicked'		: self.on_subformat_remove_clicked,
		'on_subformat_rename_clicked'		: self.on_subformat_rename_clicked,
		'on_subformat_name_combo_changed'	: self.on_subformat_name_combo_changed,
		# media
		'on_medium_add_clicked'			: self.on_medium_add_clicked,
		'on_medium_remove_clicked'		: self.on_medium_remove_clicked,
		'on_medium_rename_clicked'		: self.on_medium_rename_clicked,
		'on_medium_name_combo_changed'		: self.on_medium_name_combo_changed,
		# video codecs
		'on_vcodec_add_clicked'			: self.on_vcodec_add_clicked,
		'on_vcodec_remove_clicked'		: self.on_vcodec_remove_clicked,
		'on_vcodec_rename_clicked'		: self.on_vcodec_rename_clicked,
		'on_vcodec_name_combo_changed'		: self.on_vcodec_name_combo_changed
	})#}}}

def connect_add_signals(self):#{{{
	try:
		self.widgets['results']['select'].disconnect(self.poster_results_signal)
	except:
		pass

	try:
		self.widgets['results']['treeview'].disconnect(self.results_poster_double_click)
	except:
		pass

	try:
		self.widgets['results']['select'].disconnect(self.widgets['results']['signal'])
	except:
		pass

	try:
		self.widgets['results']['treeview'].disconnect(self.results_double_click)
	except:
		pass

	# connect signals
	self.widgets['results']['signal'] = self.widgets['results']['select'].connect('clicked', \
			self.populate_dialog_with_results)
	self.results_double_click = self.widgets['results']['treeview'].connect('button_press_event', \
		self.on_results_button_press_event)#}}}

def connect_poster_signals(self, event, result, current_poster):#{{{
	import edit

	try:
		self.widgets['results']['select'].disconnect(self.poster_results_signal)
	except:
		pass

	try:
		self.widgets['results']['treeview'].disconnect(self.results_poster_double_click)
	except:
		pass

	try:
		self.widgets['results']['select'].disconnect(self.widgets['results']['signal'])
	except:
		pass

	try:
		self.widgets['results']['treeview'].disconnect(self.results_double_click)
	except:
		pass

	# connect signals

	self.results_poster_double_click = self.widgets['results']['treeview'].connect('button_press_event', \
		edit.get_poster_select_dc, self, result, current_poster)

	self.poster_results_signal = \
		self.widgets['results']['select'].connect('clicked', edit.get_poster_select, \
		self, result, current_poster)
	#}}}
# vim: fdm=marker
