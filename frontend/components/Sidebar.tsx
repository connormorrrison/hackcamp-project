"use client"

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const sampleConversations = [
  { id: 1, title: "Help with React hooks" },
  { id: 2, title: "Dark mode implementation" },
  { id: 3, title: "TypeScript best practices" },
  { id: 4, title: "Next.js routing guide" },
  { id: 5, title: "API integration tips" },
  { id: 6, title: "Styling with Tailwind" },
  { id: 7, title: "Component architecture" },
];

export function Sidebar() {
  const [selectedId, setSelectedId] = useState<number | null>(1);

  return (
    <div className="p-8">
      <Card className="w-65 h-[calc(100vh-4rem)] rounded-2xl">
        <CardHeader>
          <CardTitle className="text-lg font-normal">Chats</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {sampleConversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => setSelectedId(conversation.id)}
              className={`px-2 py-2 rounded-xl cursor-pointer transition-colors ${
                selectedId === conversation.id
                  ? "bg-gray-600/8 text-gray-400"
                  : "text-foreground hover:bg-gray-600/5"
              }`}
            >
              <p className="text-base font-normal truncate">{conversation.title}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
