#!/bin/sh

# We need this to get the application path
name="`basename $0`"
tmp="`pwd`/$0"
tmp="`dirname $tmp`"
bundle="`dirname $tmp`"
bundle_contents="$bundle"
bundle_res="$bundle_contents"/Resources
bundle_lib="$bundle_res"/lib
bundle_bin="$bundle_res"/bin
bundle_data="$bundle_res"/share
bundle_etc="$bundle_res"/etc

# We need to export the paths so that GTK works well
export PYTHONPATH="/Library/gtk/lib/python2.6/site-packages/"
export PYTHON="$bundle_contents/MacOS/python"
PYTHON="$bundle_contents/MacOS/python"
export VERSIONER_PYTHON_PREFER_32_BIT=yes
export GDK_PIXBUF_MODULE_FILE="/Library/gtk/etc/gtk-2.0/gdk-pixbuf.loaders"
export GTK2_RC_FILES="/Library/gtk/etc/gtk-2.0/gtkrc"
export GTK_DATA_PREFIX="/Library/gtk"
export GTK_EXE_PREFIX="/Library/gtk"
export GTK_IM_MODULE_FILE="/Library/gtk/etc/gtk-2.0/gtk.immodules"
export GTK_PATH="/Library/gtk"
export XDG_DATA_DIRS="/Library/gtk/share"

# We need a UTF-8 locale.
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# Here we call the python script
exec $PYTHON "$bundle_contents/Resources/griffith"