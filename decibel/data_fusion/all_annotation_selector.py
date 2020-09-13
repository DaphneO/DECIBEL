from decibel.data_fusion.annotation_selector_interface import AnnotationSelectorInterface


class AllAnnotationSelector(AnnotationSelectorInterface):
    def select_annotations(self, input_annotations):
        return input_annotations
