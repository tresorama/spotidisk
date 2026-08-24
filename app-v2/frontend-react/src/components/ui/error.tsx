import { AxiosError } from "axios";

export function ErrorRenderer({ error }: { error: Error | AxiosError; }) {
  if (error instanceof AxiosError) {
    const name = error.name;
    const message = error.message;
    const code = error.code;
    const data = JSON.stringify(error.response?.data ?? {}, null, 2);
    return (
      <div>
        <p>{name}</p>
        <p>{message}</p>
        <p>{code}</p>
        <p>{data}</p>
      </div>
    );
  }

  const name = error.name;
  const message = error.message;
  return (
    <div>
      <p>{name}</p>
      <p>{message}</p>
    </div>
  );
}