import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Props {
  text: string;
}

export default function StreamingText({ text }: Props) {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] rounded-2xl rounded-bl-sm px-4 py-3 bg-surface-light border border-border">
        <div className="markdown-content text-sm">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
        </div>
        <span className="inline-block w-2 h-4 bg-accent animate-pulse ml-0.5" />
      </div>
    </div>
  );
}
