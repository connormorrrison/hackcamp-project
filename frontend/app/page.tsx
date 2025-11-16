import "./global.css";
import { URLBar } from "./URLBar/URLBar";
import { PDFUpload } from "./PDFUpload/PDFUpload";

export default function Home() {
  return (
    <div>
      <URLBar />
      <PDFUpload />
    </div>
  );
}
