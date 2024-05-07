from agent.string_utils import StringUtils


class TestStringUtils:
    @staticmethod
    def test_inject_suffix_no_extension():
        filename = "myfile"
        suffix = "-suffix"
        expected = "myfile-suffix"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected

    @staticmethod
    def test_inject_suffix_with_extension():
        filename = "myfile.txt"
        suffix = "-suffix"
        expected = "myfile-suffix.txt"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected

    @staticmethod
    def test_inject_suffix_multiple_dots():
        filename = "my.file.name.txt"
        suffix = "-suffix"
        expected = "my.file.name-suffix.txt"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected

    @staticmethod
    def test_inject_suffix_empty_filename():
        filename = ""
        suffix = "-suffix"
        expected = "-suffix"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected

    @staticmethod
    def test_inject_suffix_empty_suffix():
        filename = "myfile.txt"
        suffix = ""
        expected = "myfile.txt"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected

    @staticmethod
    def test_inject_suffix_long_suffix():
        filename = "myfile.txt"
        suffix = "-verylongsuffix"
        expected = "myfile-verylongsuffix.txt"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected

    @staticmethod
    def test_inject_suffix_special_characters():
        filename = "my file.txt"
        suffix = "-suffix"
        expected = "my file-suffix.txt"
        assert StringUtils.add_filename_suffix(filename, suffix) == expected
