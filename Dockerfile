# DESCRIPTION:	Create griffith container with its dependencies
# USAGE:
#	# Build griffith image
#	docker build -t griffith .
#
#	# Run the container and mount path to griffith config
#	docker run -it \
#       -v $HOME/.griffith:/home/griffith/.griffith \
#		-v /tmp/.X11-unix:/tmp/.X11-unix \
#		-e DISPLAY=$DISPLAY \
#		griffith "$@"
#
# ISSUES:
#	# 'Gtk: cannot open display: :0'
#	Try to set 'DISPLAY=your_host_ip:0' or run 'xhost +' on your host.
#	see: https://stackoverflow.com/questions/28392949/running-chromium-inside-docker-gtk-cannot-open-display-0
#

FROM debian:9-slim

RUN useradd -m griffith
WORKDIR /home/griffith
CMD ["/usr/bin/griffith"]

RUN apt-get update && apt-get install -y \
	griffith \
	--no-install-recommends \
	&& rm -rfv /var/lib/apt/lists/*

USER griffith
