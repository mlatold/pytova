Pytova
======

#### About
Open source forum software written in Python
 *   A forum that uses the almost-latest in web technologies. Heavy use on Ajax, CSS3, and Python. By beta the site will support basic functionality with javascript disabled, however it is assumed that if you have an account and are using typical features of a logged in user, you have a fairly modern browser with javascript enabled. Ideally though, the forum works everywhere with a responsive layout (you can shrink and enlarge your browsers window to see this in action). All the current other forum softwares were designed in an era before these new web technologies, so they don't utilize them. So you should have an excellent experience on phone, tablet and desktop computer. Touch screens will NOT be a problem.
 *   IE8 and lower will not be supported. IE9 will be supported closer to the forums beta date. IE10 should load but I'm only testing in firefox and chrome at the moment so it's probably unpredictable.
 *   Optimization. I am utilizing all the technologies I can and making some sacrifices for the sake of making sure bandwidth isn't wasted on phones with data. Pages will always load within a fraction of a second making things better for high load servers, and pages are written to minimize overhead. Things like uploaded avatars will automatically be converted to small jpg files, and things like forum images may not show by default. This is to take into account people on data plans. There will be very little images loaded from other sources, its either pure CSS or embeded base64 encoded images.
 *   Free and open source. I have the GPL 3.0 Licence for this project. You are more than welcome to download the source and do whatever you want with it.

#### Requirements
Pytova uses [Tornado 2.4.1](http://www.tornadoweb.org) as a server.