FROM nginx:stable-alpine
# Copy whole frontend folder into nginx html root
COPY . /usr/share/nginx/html/
# Ensure nginx site config (if you have one)
COPY default.conf /etc/nginx/conf.d/default.conf
