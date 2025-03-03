import tiktoken

# Load tokenizer for OpenAI models (GPT-4/GPT-3.5)
encoding = tiktoken.get_encoding("cl100k_base")

# Article text
article_text = """ 
Donald Trump Names XRP, SOL, ADA, BTC and ETH as Part of U.S. Crypto Reserve
The U.S. president provided the first details about what a crypto reserve may look like.
By Nikhilesh De, Sam Kessler|Edited by Aoyon Ashraf
Updated Mar 2, 2025, 5:32 p.m. UTCPublished Mar 2, 2025, 3:43 p.m. UTC
President Donald Trump
What to know:
U.S. President Donald Trump announced that XRP, Solana, and Cardano would be included in a U.S. strategic crypto reserve.
He later added Bitcoin and Ethereum to the list of assets composing the reserve.
XRP, SOL, and ADA experienced significant price surges on the news, while BTC and ETH fans expressed disappointment and surprise as they weren't added in the first announcement.

U.S. President Donald Trump named XRP, Solana (SOL) and Cardano (ADA) as three assets to be included in a U.S. strategic crypto reserve on Sunday, providing the first details about what such a reserve may look like.

STORY CONTINUES BELOW
Don't miss another story.
Subscribe to the State of Crypto Newsletter today. See all newsletters
Enter your Email
By signing up, you will receive emails about CoinDesk products and you agree to our terms of use and privacy policy.
Notably, Trump did not initially mention bitcoin (BTC) or Ethereum (ETH) — the two largest cryptocurrencies by market capitalization — in his statement, but he later clarified that the reserve would include these assets as well. Trump made the announcements on Truth Social, his social media platform.

"A U.S. Crypto Reserve will elevate this critical industry after years of corrupt attacks by the Biden Administration, which is why my Executive Order on Digital Assets directed the Presidential Working Group to move forward on a Crypto Strategic Reserve that includes XRP, SOL, and ADA," Trump stated. "I will make sure the U.S. is the Crypto Capital of the World. We are MAKING AMERICA GREAT AGAIN!"

(Truth Social)
(Truth Social)
Following Trump's initial announcement, XRP, SOL, and ADA experienced significant price surges. The price of ADA soared by more than 63% within two hours after the president's post, while SOL increased by 23% and XRP by 32%.


While fans of XRP, ADA and SOL celebrated the news, some BTC and ETH fans initially responded with a mixture of disappointment and surprise.

BREAKING: 🇺🇸 President Trump snatches defeat from the jaws of victory — announces he's creating a "Crypto Strategic Reserve", without mention of Bitcoin. pic.twitter.com/Tpl0zdOd7G

— Swan (@Swan) March 2, 2025
Around an hour after his initial post, the president clarified that "BTC and ETH, as other valuable Cryptocurrencies, will be at the heart of the Reserve."

Trump has been discussing the idea of a strategic crypto reserve since his 2024 presidential campaign. Soon after taking office in January, he signed an executive order directing a working group to evaluate the formation of a strategic crypto reserve, but the order did not explicitly mandate that the U.S. establish one outright.

The order said the digital assets working group should "evaluate the potential creation and maintenance of a national digital asset stockpile." Trump said on Sunday that the group should "move forward" with formally establishing the reserve. The working group will host a summit on Friday with crypto industry and government representatives.

Sen. Cynthia Lummis previously introduced a bill to create a strategic bitcoin reserve for the U.S. She first advocated for one at July's Bitcoin Nashville conference, where then-candidate Trump also spoke. The bill proposed by Lummis would have authorized the U.S. Treasury to acquire one million bitcoins over five years, equating to approximately 5% of the total Bitcoin supply.


A number of U.S. state legislatures have already introduced bills to create their own strategic crypto reserves, though most of these efforts have failed to take off.

David Sacks, the White House crypto and AI czar, is a limited partner of Multicoin Capital, which is invested in Solana, a blockchain ecosystem focused on providing low fees and fast transactions. Sacks said in a 2021 interview that he was "hodling" SOL, the blockchain's native token. TRUMP, the president's memecoin, is also built on Solana.

Sacks said on X (formerly Twitter) that Trump's announcement was "consistent with his week-one EO" shortly after Trump's posts.

Ripple, meanwhile, is in the midst of a years-long legal battle with the U.S. Securities and Exchange Commission, which charged the company with selling XRP — the native token of the Ripple-supported XRP Ledger blockchain — as an unregistered security during Trump's first term. In recent months, Ripple has sought to increase its profile in Washington, including by contributing heavily to Fairshake, a crypto industry super PAC, as well as to Trump's 2025 inaugural fund.

UPDATE (March 2, 2025, 16:50 UTC): Adds additional information and Trump's second post.

UPDATE (March 2, 17:15 UTC): Adds additional information and responses."""

# Token counting
token_count = len(encoding.encode(article_text))
print("Token count:", token_count)