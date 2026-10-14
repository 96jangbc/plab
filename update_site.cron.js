// Polestar4 사이트 자동 업데이트 — build + commit + push
// cron script payload는 객체를 반환해야 하므로 명시적으로 return 한다.
await exec({ command: "bash /Users/jangbc/.openclaw/workspace/polestar-site/update_site.sh" });
return {};
