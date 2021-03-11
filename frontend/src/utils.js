/* eslint-disable no-bitwise */

export default function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0; const
      // eslint-disable-next-line no-mixed-operators
      v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}