const GRADIENT_SPAN =
  '<span class="bg-gradient-to-r from-[#7C3AED] to-[#06B6D4] bg-clip-text text-transparent">klangbild</span>';

export const useGradientBrand = () => {
  const highlight = (text: string) => text.replace(/klangbild/g, GRADIENT_SPAN);

  return { highlight };
};
