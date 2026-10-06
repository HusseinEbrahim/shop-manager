const currency = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" });

export function formatMoney(value) {
  return currency.format(Number(value));
}