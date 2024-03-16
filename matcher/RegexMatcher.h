#ifndef REGEXMATCHER_H
#define REGEXMATCHER_H

#include <iostream>
#include <regex>
#include <string>
#include <vector>
#include <algorithm>
#include <iterator>
#include <chrono>
#include <thread>

class RegexMatcher {
public:
    RegexMatcher(const std::string& text, const std::vector<std::string>& patterns);
    ~RegexMatcher();

    void match();

private:
    std::vector<std::regex> compileRegexPatterns(const std::vector<std::string>& patterns);
    std::vector<std::string> regexMatching(const std::string& text, const std::vector<std::regex>& compiledPatterns);

    std::string text_;
    std::vector<std::string> patterns_;
    std::vector<std::regex> compiledPatterns_;
    std::vector<std::string> matches_;
};

#endif // REGEXMATCHER_H
