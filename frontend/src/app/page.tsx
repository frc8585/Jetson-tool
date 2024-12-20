// src/app/page.tsx

import { redirect } from "next/navigation";

const Page = () => {
  // 使用 redirect 進行重定向
  redirect("/dashboard"); // 將用戶重定向到 /dashboard

  return <div>Redirecting...</div>; // 這部分其實不會顯示出來，因為重定向會立即發生
};

export default Page;
