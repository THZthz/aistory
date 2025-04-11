import React, {useEffect, useRef, useState} from "react"
import '../styles/flataccordion.css'

export interface FASubItemProps {
    id: string;
    title: string;
    subtitle?: string;
    icon?: string;
}

export interface FAItemProps {
    id: string;
    icon?: string | any;
    title: string | any;
    subtitle: string | any;
    meta?: string | any;
    onClick?: () => void;
    subItems?: FASubItemProps[];
}

export interface FAProps {
    items?: FAItemProps[];
    initialWidth?: number;
    initialHeight?: number;
    showCount?: boolean;
    resizable?: boolean;
}

const FlatAccordion: React.FC<FAProps> = (
    {
        items,
        initialWidth = 300,
        initialHeight = 300,
        showCount = true,
        resizable = true,
    }) => {

    const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
    const [selectedSubItems, setSelectedSubItems] = useState<Set<string>>(new Set());
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
    const [dimensions, setDimensions] = useState({
        height: initialHeight,
        width: initialWidth
    });
    const [isResizing, setIsResizing] = useState(false);
    const [resizeDirection, setResizeDirection] = useState<"vertical" | "horizontal" | "both" | null>(null);
    const [containerWidth, setContainerWidth] = useState<number | null>(null);

    const containerRef = useRef<HTMLDivElement>(null);
    const parentRef = useRef<HTMLElement | null>(null);

    // Get the bounds of parent element.
    useEffect(() => {
        if (containerRef.current) {
            parentRef.current = containerRef.current.parentElement;
        }
    }, []);

    const isParentFullySelected = (item: FAItemProps) => {
        if (!item.subItems || item.subItems.length === 0) {
            return selectedItems.has(item.id);
        }
        return item.subItems.every(subItem => selectedSubItems.has(subItem.id));
    };

    const isParentPartiallySelected = (item: FAItemProps) => {
        if (!item.subItems || item.subItems.length === 0) return false;
        const hasSelected = item.subItems.some(subItem => selectedSubItems.has(subItem.id));
        const hasUnselected = item.subItems.some(subItem => !selectedSubItems.has(subItem.id));
        return hasSelected && hasUnselected;
    };

    const toggleParentSelection = (item: FAItemProps) => {
        const newSelectedItems = new Set(selectedItems);
        const newSelectedSubItems = new Set(selectedSubItems);

        const shouldSelect = !isParentFullySelected(item);

        if (shouldSelect) {
            newSelectedItems.add(item.id);
            if (item.subItems) {
                item.subItems.forEach(subItem => newSelectedSubItems.add(subItem.id));
            }
        } else {
            newSelectedItems.delete(item.id);
            if (item.subItems) {
                item.subItems.forEach(subItem => newSelectedSubItems.delete(subItem.id));
            }
        }

        setSelectedItems(newSelectedItems);
        setSelectedSubItems(newSelectedSubItems);
    };

    const toggleSubItemSelection = (subItemId: string, parentId: string) => {
        const newSelectedSubItems = new Set(selectedSubItems);

        if (newSelectedSubItems.has(subItemId)) {
            newSelectedSubItems.delete(subItemId);
        } else {
            newSelectedSubItems.add(subItemId);
        }

        const parentItem = items?.find(item => item.id === parentId);
        if (parentItem) {
            const allSubItemsSelected = parentItem.subItems?.every(sub => newSelectedSubItems.has(sub.id));
            const newSelectedItems = new Set(selectedItems);

            if (allSubItemsSelected) {
                newSelectedItems.add(parentId);
            } else {
                newSelectedItems.delete(parentId);
            }

            setSelectedItems(newSelectedItems);
        }

        setSelectedSubItems(newSelectedSubItems);
    };

    const toggleItemExpansion = (itemId: string) => {
        const newExpandedItems = new Set(expandedItems);
        if (newExpandedItems.has(itemId)) {
            newExpandedItems.delete(itemId);
        } else {
            newExpandedItems.add(itemId);
        }
        setExpandedItems(newExpandedItems);
    };

    const startResize = (e: React.MouseEvent | React.TouchEvent, direction: "vertical" | "horizontal" | "both") => {
        if (!resizable) return;
        setIsResizing(true);
        setResizeDirection(direction);
        e.preventDefault();
        e.stopPropagation();
    };

    useEffect(() => {
        if (containerRef.current && !containerWidth) {
            setContainerWidth(containerRef.current.offsetWidth);
        }
    }, [expandedItems]);

    useEffect(() => {
        const getClientX = (e: MouseEvent | TouchEvent): number => {
            return 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
        }

        const getClientY = (e: MouseEvent | TouchEvent): number => {
            return 'touches' in e ? e.touches[0].clientY : (e as MouseEvent).clientY;
        };

        const handleMove = (e: MouseEvent | TouchEvent) => {
            if (!isResizing || !containerRef.current || !parentRef.current) return;

            const containerRect = containerRef.current.getBoundingClientRect();
            const parentRect = parentRef.current.getBoundingClientRect();

            // Maximum sizes available.
            const maxWidth = parentRect.right - containerRect.left - 10; // 10px spacing
            const maxHeight = parentRect.bottom - containerRect.top - 10;

            let newWidth = dimensions.width;
            let newHeight = dimensions.height;

            if (resizeDirection === "vertical" || resizeDirection === "both") {
                const clientY = getClientY(e);
                newHeight = Math.min(
                    Math.max(clientY - containerRect.top, 100), // Minimum height.
                    maxHeight
                );
            }

            if (resizeDirection === "horizontal" || resizeDirection === "both") {
                const clientX = getClientX(e);
                newWidth = Math.min(
                    Math.max(clientX - containerRect.left, 200), // Minimum height.
                    maxWidth
                );
            }

            setDimensions({
                width: newWidth,
                height: newHeight
            });
        };

        const handleEnd = () => {
            setIsResizing(false);
            setResizeDirection(null);
        };

        if (isResizing) {
            document.addEventListener('mousemove', handleMove);
            document.addEventListener('mouseup', handleEnd);
            document.addEventListener('touchmove', handleMove);
            document.addEventListener('touchend', handleEnd);
        }

        return () => {
            document.removeEventListener('mousemove', handleMove);
            document.removeEventListener('mouseup', handleEnd);
            document.removeEventListener('touchmove', handleMove);
            document.removeEventListener('touchend', handleEnd);
        };
    }, [isResizing, resizeDirection, dimensions]);

    const totalSelectedCount = items ?
        Array.from(selectedItems).length +
        Array.from(selectedSubItems).length : 0;

    return (
        <div ref={containerRef} className="facd-container" style={{
            height: `${dimensions.height}px`,
            width: `${dimensions.width}px`,
            minWidth: `${dimensions.width}px`,
            maxWidth: "100%", // Make sure we dont overflow our parent element.
        }}>
            <div className="facd-list-container">
                <div className="facd-list">
                    {items && items.map(item => (
                        <React.Fragment key={item.id}>
                            <div
                                className={`facd-item ${isParentFullySelected(item) ? 'selected' : ''} ${isParentPartiallySelected(item) ? 'partially-selected' : ''}`}
                                onClick={() => toggleParentSelection(item)}
                            >
                                <div className="facd-item-header">
                                    <div className="facd-item-icon">{item.icon || '•'}</div>
                                    <div className="facd-item-content">
                                        <div className="facd-item-title" title={item.title}>
                                            {item.title}
                                        </div>
                                        {item.subtitle && (
                                            <div className="facd-item-subtitle" title={item.subtitle}>
                                                {item.subtitle}
                                            </div>
                                        )}
                                    </div>
                                    <div className="facd-item-meta">
                                        {item.meta && (
                                            <div className="facd-meta-text" title={item.meta}>
                                                {item.meta}
                                            </div>
                                        )}
                                        {item.subItems && (
                                            <button
                                                className={`facd-arrow-btn ${expandedItems.has(item.id) ? 'expanded' : ''}`}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    toggleItemExpansion(item.id);
                                                }}
                                                aria-label={expandedItems.has(item.id) ? "Collapse" : "Expand"}
                                            >
                                                <svg className="facd-arrow-icon" viewBox="0 0 24 24">
                                                    <path fill="currentColor"
                                                          d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"/>
                                                </svg>
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {expandedItems.has(item.id) && item.subItems && item.subItems.map(subItem => (
                                <div
                                    key={subItem.id}
                                    className={`facd-subitem ${selectedSubItems.has(subItem.id) ? 'selected' : ''}`}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        toggleSubItemSelection(subItem.id, item.id);
                                    }}
                                >
                                    <div className="facd-subitem-content">
                                        <div className="facd-subitem-title" title={subItem.title}>
                                            {subItem.title}
                                        </div>
                                        {subItem.subtitle && (
                                            <div className="facd-subitem-subtitle" title={subItem.subtitle}>
                                                {subItem.subtitle}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </React.Fragment>
                    ))}
                </div>
            </div>

            {resizable && (
                <>
                    <div
                        className="facd-resize-handle vertical"
                        onMouseDown={(e) => startResize(e, "vertical")}
                        onTouchStart={(e) => startResize(e, "vertical")}
                    />
                    <div
                        className="facd-resize-handle horizontal"
                        onMouseDown={(e) => startResize(e, "horizontal")}
                        onTouchStart={(e) => startResize(e, "horizontal")}
                    />
                    <div
                        className="facd-resize-handle corner"
                        onMouseDown={(e) => startResize(e, "both")}
                        onTouchStart={(e) => startResize(e, "both")}
                    />
                </>
            )}

            {(showCount && items) && (
                <div className="facd-count">
                    {totalSelectedCount} items selected
                    {selectedItems.size > 0 && ` (${selectedItems.size} parent items)`}
                </div>
            )}
        </div>
    );
};

export default FlatAccordion;
