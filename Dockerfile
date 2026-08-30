FROM nginx:alpine

# カスタムNginx設定を配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# アプリケーションファイルをコピー
COPY . /usr/share/nginx/html

# Nginx実行ユーザーが読み取れるように権限を設定
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

