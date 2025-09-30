#' Calculate Standard Deviation
#'
#' This function calculates the standard deviation of a numeric vector
#' using the sample standard deviation formula (n-1 denominator).
#'
#' @param x A numeric vector for which to calculate standard deviation.
#'   Missing values (NA) are removed before calculation.
#' @param na.rm Logical value indicating whether NA values should be
#'   removed before computation. Default is TRUE.
#' @return A numeric value representing the standard deviation of x.
#'   Returns NA if the vector is empty or has less than 2 elements.
#' @examples
#' # Basic usage
#' data <- c(1, 2, 3, 4, 5)
#' calc_sd(data)
#' # Output: 1.58
#'
#' # With missing values
#' data_na <- c(1, 2, NA, 4, 5)
#' calc_sd(data_na)
#' @export
calc_sd <- function(x, na.rm = TRUE) {
  if (na.rm) {
    x <- x[!is.na(x)]
  }
  if (length(x) < 2) {
    return(NA)
  }
  return(sd(x))
}

#' Filter Data Frame by Threshold
#'
#' Filters a data frame to keep only rows where a specified column
#' exceeds a given threshold value.
#'
#' @param df A data frame to filter
#' @param column Character string specifying the column name to filter on
#' @param threshold Numeric threshold value for filtering
#' @return A data frame containing only rows where the specified column
#'   value exceeds the threshold
#' @examples
#' df <- data.frame(x = 1:5, y = c(10, 20, 30, 40, 50))
#' filter_by_threshold(df, "y", 25)
#' @export
filter_by_threshold <- function(df, column, threshold) {
  return(df[df[[column]] > threshold, ])
}