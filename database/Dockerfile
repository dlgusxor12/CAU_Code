FROM postgres:15-alpine

# 한국어 로케일 설정 (선택사항)
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 초기화 스크립트 복사 (번호 순서대로 실행됨)
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql
COPY schemas/schema.sql /docker-entrypoint-initdb.d/02-schema.sql

# 포트 노출
EXPOSE 5432