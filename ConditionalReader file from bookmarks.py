# -*- coding: utf-8 -*-
"""
Generate a ConditionalReader file from the video bookmarks
    
This macro takes the list of the current video bookmarks and generates a 
new text file to be used with ConditionalReader.  Each frame can represent a 
single frame or the start or end of a range of frames.  If the 'interpolation' 
option is selected (only valid for int and float), 'Value' must consist in 
two space-separated values.

If a bookmark have a title, it can be used as its value instead of the one 
introduced in the prompt dialog.  For ranges of frames, the value can be put 
in the title of either the start or end frame.  When using interpolation the 
two values can be introduced both in the same bookmark or separately.

More info on ConditionalReader:
http://avisynth.org/mediawiki/ConditionalReader


Date: 2012-11-27
Latest version:
  https://github.com/vdcrim/avsp-macros
Original macro idea from Bernardd:
  http://forum.doom9.org/showpost.php?p=1562538&postcount=738

Changelog:
- fix
- change some defaults, improve the macro description
- accept introducing the two values needed for interpolation separately 
- check if there are bookmarks before showing the prompt
- minor fixes
- warn if an output path has not been introduced instead of just exiting
- save introduced values for showing the dialog again if interpolation is
  selected but not Int or Float, and for the case above
- fix Python 2.6 compatibility


Copyright (C) 2012  Diego Fernández Gosende <dfgosende@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along 
with this program.  If not, see <http://www.gnu.org/licenses/gpl-2.0.html>.

"""

# PREFERENCES

default_type = 'Bool'
default_default = ''
default_value = ''
default_bm_meaning = 'Single frames'
default_use_title = True
default_filename = ur''  #  ur''  ->  avs filename + suffix
suffix = '.cr.txt'
default_insert_path = True


# ------------------------------------------------------------------------------


# Run in thread
import sys
import os.path

self = avsp.GetWindow()

# Get the bookmarks
bmlist = avsp.GetBookmarkList(title=True)
if not bmlist:
    avsp.MsgBox(_('There is not bookmarks'), _('Error'))
    return
bmlist.sort()

# Prompt for options
if not default_filename:
    if self.version > '2.3.1':
        default_filename = avsp.GetScriptFilename(propose='general')
    else:
        default_filename = os.path.join(self.options['recentdir'], 
            self.scriptNotebook.GetPageText(self.scriptNotebook.GetSelection()).lstrip('* '))
default_filename2, ext = os.path.splitext(default_filename)
if ext in ('.avs', '.avsi'):
    default_filename = default_filename2
default_filename += suffix
txt_filter = (_('Text files') + ' (*.txt)|*.txt|' + _('All files') + '|*.*')
while True:
    options = avsp.GetTextEntry(
        title=_('ConditionalReader file from bookmarks'), 
        message=[[_('Type'), _('Default'), _('Value')], 
                 [_('Bookmarks represent...'), 
                  _("Override 'Value' with the bookmark's title")], 
                 _('ConditionalReader file'), 
                 _('Insert the ConditionalReader file path at the current '
                   'cursor position')
                ], 
        default=[[(_('Bool'), _('Int'), _('Float'), _('String'), default_type), 
                  (_('True'), _('False'), default_default), 
                  (_('True'), _('False'), default_value)], 
                 [(_('Single frames'), _('Ranges of frames'), 
                   _('Ranges of frames (with interpolation)'), default_bm_meaning), 
                   default_use_title], 
                 (default_filename, txt_filter), default_insert_path
                ], 
        types=[['list_read_only', 'list_writable', 'list_writable'], 
               ['list_read_only', 'check'], 'file_save', 'check'], 
        width=415)
    if not options:
        return
    type, default, value, bm_meaning, use_title, filename, insert_path = options
    if not filename:
        avsp.MsgBox(_('An output path is needed'), _('Error'))
    elif (bm_meaning == _('Ranges of frames (with interpolation)') and 
          type not in (_('Int'), _('Float'))):
        avsp.MsgBox(_('Interpolation only available for Int and Float'), _('Error'))
    else: break
    (default_type, default_default, default_value, default_bm_meaning, 
     default_use_title, default_filename, default_insert_path) = options

# Write the ConditionalReader file
value_default = value.strip()
text = ['Type {0}\n'.format(type)]
if default: text.append(u'Default {0}\n'.format(default.strip()))
if bm_meaning == _('Single frames'):
    for frame, title in bmlist:
        text.append(u'{0} {1}\n'.format(frame, 
                    title.strip() if use_title and title else value_default))
else:
    if len(bmlist) % 2 and not avsp.MsgBox(_('Odd number of bookmarks'), 
                                           title=_('Warning'), cancel=True):
        return
    prefix = 'R' if bm_meaning == _('Ranges of frames') else 'I'
    for i, bm in enumerate(bmlist):
        if i%2:
            value = None
            if use_title:
                if bmlist[i-1][1]:
                    value = bmlist[i-1][1].strip()
                if bm[1]:
                    if value and bm_meaning != _('Ranges of frames'):
                        value += ' ' + bm[1].strip()
                    else:
                        value = bm[1].strip()
                if not value:
                    value = value_default
            else:
                value = value_default
            text.append(u'{0} {1} {2} {3}\n'.format(
                        prefix, bmlist[i-1][0], bm[0], value))
text = [line.encode(sys.getfilesystemencoding()) for line in text]
with open(filename, 'w') as file:
    file.writelines(text)
if insert_path:
    avsp.InsertText(u'"{0}"'.format(filename), pos=None)
