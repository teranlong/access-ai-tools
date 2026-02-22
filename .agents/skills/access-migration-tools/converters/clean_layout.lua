
-- clean_layout.lua
-- 1. Remove table column widths
-- 2. Unwrap simple paragraphs in table cells and list items
-- 3. Compact lists (no blank lines between items)
-- 4. Flatten complex tables into simple pipe-compatible ones

local prefer_pipe_tables = false

function Pandoc(doc)
  if doc.meta['prefer-pipe-tables'] then
    local val = doc.meta['prefer-pipe-tables']
    if val == true or (val.t == 'MetaBool' and val.c == true) or (val.t == 'MetaString' and val.c == 'true') then
      prefer_pipe_tables = true
    end
  end
  return doc
end

-- Helper to convert all blocks in a cell into a single flat Inline list
local function flatten_blocks(blocks)
  local inlines = {}
  for i, block in ipairs(blocks) do
    if block.t == 'Para' or block.t == 'Plain' then
      for _, inline in ipairs(block.content) do
        table.insert(inlines, inline)
      end
    elseif block.t == 'BulletList' or block.t == 'OrderedList' then
      for _, item_blocks in ipairs(block.content) do
        table.insert(inlines, pandoc.Str("- "))
        local flat_item = flatten_blocks(item_blocks)
        for _, inline in ipairs(flat_item[1].content) do
          table.insert(inlines, inline)
        end
        table.insert(inlines, pandoc.Space())
      end
    end
    if i < #blocks then table.insert(inlines, pandoc.Space()) end
  end
  -- Replace LineBreaks with spaces for pipe tables
  for i, inline in ipairs(inlines) do
    if inline.t == 'LineBreak' or inline.t == 'SoftBreak' then
      inlines[i] = pandoc.Space()
    end
  end
  return {pandoc.Plain(inlines)}
end

-- Force lists to be compact by converting all Para blocks into Plain
-- within BulletList and OrderedList elements.
-- Pandoc's Markdown writer treats a list as "loose" (double spaced) if it contains Para blocks.
local function compactify_list(list)
  return list:walk {
    Para = function(p)
      return pandoc.Plain(p.content)
    end
  }
end

function BulletList(elem)
  return compactify_list(elem)
end

function OrderedList(elem)
  return compactify_list(elem)
end

function TableCell(cell)
  if prefer_pipe_tables then
    return pandoc.TableCell(flatten_blocks(cell.contents))
  end
  
  -- For Hi-Fi mode, still unwrap to reduce vertical sprawl
  local new_contents = {}
  for _, block in ipairs(cell.contents) do
    if block.t == 'Para' then
      table.insert(new_contents, pandoc.Plain(block.content))
    else
      table.insert(new_contents, block)
    end
  end
  return pandoc.TableCell(new_contents)
end

function Table(elem)
  -- Remove width from the table itself
  if elem.attr and elem.attr.attributes then
    elem.attr.attributes.width = nil
  end

  -- Force column widths to 0 (auto) and alignment to AlignDefault
  local new_colspecs = {}
  for _, colspec in ipairs(elem.colspecs) do
    table.insert(new_colspecs, {pandoc.AlignDefault, 0})
  end
  elem.colspecs = new_colspecs
  return elem
end
