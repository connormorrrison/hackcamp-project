import { Button } from "@/components/ui/button";
import { ArrowUpIcon } from "lucide-react";

export function Button1() {
  return (
    <Button variant="outline" className="rounded-2xl h-12 text-base">
      Upload Resume
      <ArrowUpIcon />
    </Button>
  );
}
