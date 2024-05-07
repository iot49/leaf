export async function sleep_ms(duration_ms: number) {
  let promise = new Promise((resolve, _) => {
    setTimeout(() => resolve('done!'), duration_ms);
  });
  await promise;
}
