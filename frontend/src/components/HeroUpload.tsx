import { useState, type FormEvent } from "react";

interface HeroUploadProps {
  onSubmit: (payload: {
    prdFile: File;
    testCaseFile: File;
    sheetName?: string;
    generateMissingCases: boolean;
  }) => void;
  isPending: boolean;
}

export function HeroUpload({ onSubmit, isPending }: HeroUploadProps) {
  const [prdFile, setPrdFile] = useState<File | null>(null);
  const [testCaseFile, setTestCaseFile] = useState<File | null>(null);
  const [sheetName, setSheetName] = useState("");
  const [generateMissingCases, setGenerateMissingCases] = useState(true);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!prdFile || !testCaseFile) {
      return;
    }
    onSubmit({
      prdFile,
      testCaseFile,
      sheetName: sheetName || undefined,
      generateMissingCases,
    });
  };

  return (
    <form className="main-form-card" onSubmit={handleSubmit}>
      <label className="upload-block">
        <span className="field-title">需求文档</span>
        <div className="file-box">
          <input
            type="file"
            accept=".txt,.md,.pdf"
            onChange={(event) => setPrdFile(event.target.files?.[0] ?? null)}
          />
          <strong>{prdFile?.name ?? "未选择文件"}</strong>
        </div>
        <small>选择 txt / md / pdf 文件</small>
      </label>

      <label className="upload-block">
        <span className="field-title">测试用例</span>
        <div className="file-box">
          <input
            type="file"
            accept=".xlsx"
            onChange={(event) => setTestCaseFile(event.target.files?.[0] ?? null)}
          />
          <strong>{testCaseFile?.name ?? "未选择文件"}</strong>
        </div>
        <small>选择 xlsx 文件</small>
      </label>

      <label className="text-field">
        <span className="field-title">Sheet 名称</span>
        <input
          value={sheetName}
          onChange={(event) => setSheetName(event.target.value)}
          placeholder="为空时读取第一个 Sheet"
        />
      </label>

      <label className="check-field">
        <input
          type="checkbox"
          checked={generateMissingCases}
          onChange={(event) => setGenerateMissingCases(event.target.checked)}
        />
        <span>自动生成缺失测试用例</span>
      </label>

      <button className="primary-button large-button" type="submit" disabled={isPending || !prdFile || !testCaseFile}>
        {isPending ? "评估中..." : "开始评估"}
      </button>
    </form>
  );
}
