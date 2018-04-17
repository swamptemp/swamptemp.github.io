#!/usr/bin/Rscript

library(ggplot2)
library(lubridate)
files <- list.files("data", recursive = TRUE, full.names = TRUE)
if (length(files) > 3) {
  files <- rev(files)[1:3]
}
df <- do.call(rbind, lapply(files, function (x) read.csv(x, header = FALSE)))
names(df) <- c("dt", "temp", "o_temp", "temp1", "temp2", "humidity", "o_humidity")

df$dt <- as.POSIXct(strptime(df$dt, "%Y-%m-%d %H:%M:%S"))
df <- df[df$dt >= Sys.time() - days(2), ]
df <- df[order(df$dt), ]

plot.df <- rbind(data.frame(dt = df$dt, temp = df$temp, variable = "Ambient"),
                 data.frame(dt = df$dt, temp = df$o_temp, variable = "Outdoors"),
                 data.frame(dt = df$dt, temp = df$temp1, variable = "Fermenter 1"),
                 data.frame(dt = df$dt, temp = df$temp2, variable = "Fermenter 2"))
g <- ggplot(plot.df, aes(dt, temp)) + geom_line(aes(color = variable)) +
  xlab("") + ylab("°C") + theme_minimal() +
  theme(axis.text = element_text(family = "Roboto", size = 16),
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.title = element_text(family = "Roboto", size = 16),
        legend.text = element_text(family = "Roboto", size = 22),
        legend.position = "bottom", legend.title = element_blank())

png(filename = "/home/pi/swamptemp.github.io/images/history.png",
    height = 400, width = 800)
plot(g)
dev.off()

plot.df <- rbind(data.frame(dt = df$dt, humidity = df$humidity,
                            variable = "Indoor humidity"),
                 data.frame(dt = df$dt, humidity = df$o_humidity,
                            variable = "Outdoor humidity"))

g <- ggplot(plot.df, aes(dt, humidity)) + geom_line(aes(color = variable)) +
  xlab("") + ylab("Humidity (%)") + theme_minimal() +
  theme(axis.text = element_text(family = "Roboto", size = 16),
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.title = element_text(family = "Roboto", size = 16),
        legend.text = element_text(family = "Roboto", size = 22),
        legend.position = "bottom", legend.title = element_blank())
png(filename = "/home/pi/swamptemp.github.io/images/humidity.png",
    height = 400, width = 800)
plot(g)
dev.off()
