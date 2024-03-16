#include "RegexMatcher.h"

RegexMatcher::RegexMatcher(const std::string& text, const std::vector<std::string>& patterns)
    : text_(text), patterns_(patterns) {}

RegexMatcher::~RegexMatcher() {}

void RegexMatcher::match() {
    compiledPatterns_ = compileRegexPatterns(patterns_);

    auto start = std::chrono::high_resolution_clock::now();

    std::thread matchingThread([&]() {
        matches_ = regexMatching(text_, compiledPatterns_);
    });

    matchingThread.join();

    auto end = std::chrono::high_resolution_clock::now();

    // Print the matches
    std::cout << "Matches:" << std::endl;
    for (const auto& match : matches_) {
        std::cout << match << std::endl;
    }

    // Calculate and print the elapsed time
    std::chrono::duration<double> elapsedSeconds = end - start;
    std::cout << "Elapsed time: " << elapsedSeconds.count() << " seconds" << std::endl;
}

std::vector<std::regex> RegexMatcher::compileRegexPatterns(const std::vector<std::string>& patterns) {
    std::vector<std::regex> compiledPatterns;
    for (const auto& pattern : patterns) {
        compiledPatterns.emplace_back(pattern);
    }
    return compiledPatterns;
}

std::vector<std::string> RegexMatcher::regexMatching(const std::string& text, const std::vector<std::regex>& compiledPatterns) {
    std::vector<std::string> matches;

    try {
        for (const auto& pattern : compiledPatterns) {
            std::copy(std::sregex_token_iterator(text.begin(), text.end(), pattern, 0),
                      std::sregex_token_iterator(),
                      std::back_inserter(matches));
        }
    } catch (const std::regex_error& e) {
        std::cerr << "Regex Error: " << e.what() << std::endl;
    }

    return matches;
}
