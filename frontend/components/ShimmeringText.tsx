import { TextShimmer } from "@/components/motion-primitives/text-shimmer";

interface ShimmeringTextProps {
  isGenerating: boolean;
  documentsReady: boolean;
}

export function ShimmeringText({ isGenerating, documentsReady }: ShimmeringTextProps) {
  return (
    <div
      className={`
        text-center transition-all duration-300 ease-out
        ${isGenerating
          ? "opacity-100 max-h-12 mt-8"
          : "opacity-0 max-h-0 mt-0"
        }
      `}
    >
      {documentsReady ? (
        <p className="text-lg text-white font-medium">Documents generated</p>
      ) : (
        <TextShimmer className="text-lg">Generating your documents...</TextShimmer>
      )}
    </div>
  );
}
