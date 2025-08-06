import React, { useState } from 'react'

interface TagListProps {
  tags: string[]
  maxVisible?: number
}

const TagList: React.FC<TagListProps> = ({ tags, maxVisible = 3 }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const toggleExpansion = () => {
    setIsExpanded(!isExpanded)
  }

  const visibleTags = isExpanded ? tags : tags.slice(0, maxVisible)
  const hasMoreTags = tags.length > maxVisible

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {visibleTags.map(tag => (
        <span
          key={tag}
          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
        >
          {tag}
        </span>
      ))}
      {hasMoreTags && !isExpanded && (
        <button
          onClick={toggleExpansion}
          className="text-xs text-gray-500 hover:text-gray-700 hover:underline cursor-pointer"
        >
          +{tags.length - maxVisible} more
        </button>
      )}
      {hasMoreTags && isExpanded && (
        <button
          onClick={toggleExpansion}
          className="text-xs text-gray-500 hover:text-gray-700 hover:underline cursor-pointer"
        >
          show less
        </button>
      )}
    </div>
  )
}

export default TagList
