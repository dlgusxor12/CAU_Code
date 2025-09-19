# Node.js 20 Alpine 기반 이미지 사용 (Vite 7.1.5 호환성)
FROM node:20-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 사용자 추가 (보안 강화)
RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactuser -u 1001

# package.json과 package-lock.json 복사 (캐시 최적화)
COPY package*.json ./

# 의존성 설치 (개발 환경이므로 모든 의존성 설치)
RUN npm install && npm cache clean --force

# 소스 코드 복사
COPY . .

# 소유권 변경
RUN chown -R reactuser:nodejs /app
USER reactuser

# 포트 노출
EXPOSE 5173

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5173 || exit 1

# 개발 서버 시작
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]