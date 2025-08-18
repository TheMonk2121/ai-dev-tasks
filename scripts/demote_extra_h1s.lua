-- Demote all H1 headings after the first to H2, preserving content
local seen_h1 = false

function Header(el)
  if el.level == 1 then
    if seen_h1 then
      el.level = 2
    else
      seen_h1 = true
    end
  end
  return el
end
