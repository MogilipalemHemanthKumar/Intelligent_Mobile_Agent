import xml.etree.ElementTree as ET
import re
import os
from typing import Dict, List, Optional


class UIElementParser:
    """Analyzes UI hierarchy and identifies interactive elements"""
    
    def __init__(self):
        pass
    
    def parse_ui_hierarchy(self, xml_file_path: str) -> List[Dict]:
        """Parse UI hierarchy XML and extract interactive elements"""
        if not xml_file_path or not os.path.exists(xml_file_path):
            return []

        try:
            xml_tree = ET.parse(xml_file_path)
            root_element = xml_tree.getroot()
            parsed_elements = []

            def extract_element_data(xml_node, element_list):
                node_attributes = xml_node.attrib
                is_clickable = node_attributes.get('clickable', 'false') == 'true'
                is_scrollable = node_attributes.get('scrollable', 'false') == 'true'
                element_text = node_attributes.get('text', '').strip()
                content_description = node_attributes.get('content-desc', '').strip()
                resource_identifier = node_attributes.get('resource-id', '').strip()
                element_class = node_attributes.get('class', '').strip()
                element_bounds = node_attributes.get('bounds', '')

                if element_bounds:
                    try:
                        coordinate_matches = re.findall(r'\[(\d+),(\d+)\]', element_bounds)
                        if len(coordinate_matches) == 2:
                            top_left_x, top_left_y = map(int, coordinate_matches[0])
                            bottom_right_x, bottom_right_y = map(int, coordinate_matches[1])
                            center_x = (top_left_x + bottom_right_x) // 2
                            center_y = (top_left_y + bottom_right_y) // 2

                            # Include element if it has useful information
                            if (is_clickable or is_scrollable or element_text or content_description) and center_x > 0 and center_y > 0:
                                element_list.append({
                                    'center_x': center_x,
                                    'center_y': center_y,
                                    'display_text': element_text,
                                    'content_description': content_description,
                                    'resource_id': resource_identifier,
                                    'element_class': element_class,
                                    'is_clickable': is_clickable,
                                    'is_scrollable': is_scrollable,
                                    'bounds_string': element_bounds,
                                    'element_width': bottom_right_x - top_left_x,
                                    'element_height': bottom_right_y - top_left_y
                                })
                    except:
                        pass

                for child_node in xml_node:
                    extract_element_data(child_node, element_list)

            extract_element_data(root_element, parsed_elements)
            return parsed_elements

        except Exception as e:
            print(f"Error parsing UI hierarchy: {e}")
            return []

    def identify_search_elements(self, element_list: List[Dict]) -> List[Dict]:
        """Identify search-related UI elements with scoring"""
        search_candidates = []

        for element in element_list:
            text_content = element['display_text'].lower()
            description_content = element['content_description'].lower()
            resource_content = element['resource_id'].lower()

            # Combined text analysis
            combined_text = f"{text_content} {description_content} {resource_content}"

            relevance_score = 0

            # High priority search indicators
            if any(search_keyword in combined_text for search_keyword in ['search', 'find']):
                relevance_score += 5

            # Input field identification
            if 'edittext' in element['element_class'].lower():
                relevance_score += 4

            # Resource ID patterns
            if any(id_keyword in resource_content for id_keyword in ['search', 'query', 'input']):
                relevance_score += 3

            # Icon and button indicators
            if any(ui_keyword in combined_text for ui_keyword in ['search', 'magnify', 'glass']):
                relevance_score += 2

            # Size filtering (exclude tiny elements)
            if element['element_width'] > 200 and element['element_height'] > 30:
                relevance_score += 1

            if relevance_score > 0:
                element['search_relevance_score'] = relevance_score
                search_candidates.append(element)

        # Sort by relevance and return top candidates
        search_candidates.sort(key=lambda x: x['search_relevance_score'], reverse=True)
        return search_candidates[:5]

    def get_clickable_elements(self, element_list: List[Dict]) -> List[Dict]:
        """Filter clickable elements for fallback actions"""
        clickable_candidates = []
        
        for element in element_list:
            if element['is_clickable'] and element['element_width'] > 100:
                clickable_candidates.append(element)
        
        return clickable_candidates

    def find_elements_with_text(self, element_list: List[Dict], search_text: str) -> List[Dict]:
        """Find elements containing specific text"""
        matching_elements = []
        search_term = search_text.lower()
        
        for element in element_list:
            element_content = f"{element['display_text']} {element['content_description']}".lower()
            if search_term in element_content:
                matching_elements.append(element)
        
        return matching_elements

    def find_elements_by_class(self, element_list: List[Dict], class_name: str) -> List[Dict]:
        """Find elements by class name"""
        matching_elements = []
        target_class = class_name.lower()
        
        for element in element_list:
            if target_class in element['element_class'].lower():
                matching_elements.append(element)
        
        return matching_elements

    def generate_fallback_action(self, element_list: List[Dict], step_number: int) -> Optional[str]:
        """Generate fallback action based on available elements"""
        if not element_list:
            return None
        
        # Prioritize clickable elements
        clickable_elements = self.get_clickable_elements(element_list)
        
        if clickable_elements:
            # Cycle through elements based on step number
            selected_element = clickable_elements[step_number % len(clickable_elements)]
            element_description = selected_element['display_text'] or selected_element['content_description'] or 'interactive element'
            return f"TAP ({selected_element['center_x']},{selected_element['center_y']}) # {element_description[:30]}"
        
        return None 